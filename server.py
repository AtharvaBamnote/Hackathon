"""
FastAPI backend server for 3D Talking Avatar system.
Handles the complete pipeline: STT -> Chatbot -> TTS -> Lip-sync.
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import asyncio
import json
import os
import tempfile
import logging
from typing import Dict, List
import base64
import wave

# Import our custom modules
from stt import SpeechToText
from chatbot import MultilingualChatbot
from tts import TextToSpeech
from lip_sync import LipSyncProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="3D Talking Avatar API", version="1.0.0")

# Global instances
stt_engine = None
chatbot_engine = None
tts_engine = None
lipsync_processor = None

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize all engines on startup."""
    global stt_engine, chatbot_engine, tts_engine, lipsync_processor
    
    logger.info("Initializing 3D Talking Avatar system...")
    
    try:
        # Initialize engines
        logger.info("Loading Speech-to-Text engine...")
        stt_engine = SpeechToText(lang="en")
        
        logger.info("Loading Chatbot engine...")
        chatbot_engine = MultilingualChatbot()
        
        logger.info("Loading Text-to-Speech engine...")
        tts_engine = TextToSpeech()
        
        logger.info("Loading Lip-sync processor...")
        lipsync_processor = LipSyncProcessor()
        
        logger.info("All engines initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing engines: {e}")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page."""
    try:
        with open("frontend.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>3D Talking Avatar</title></head>
            <body>
                <h1>3D Talking Avatar System</h1>
                <p>Frontend not found. Please ensure frontend.html exists.</p>
                <p>API is running at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "engines": {
            "stt": stt_engine is not None,
            "chatbot": chatbot_engine is not None,
            "tts": tts_engine is not None,
            "lipsync": lipsync_processor is not None
        }
    }


@app.post("/api/process-text")
async def process_text(data: Dict):
    """
    Process text input through the complete pipeline.
    
    Args:
        data: JSON with 'text' and optional 'language' fields
    
    Returns:
        Complete response with audio file and viseme timeline
    """
    try:
        text = data.get("text", "")
        language = data.get("language", "en")
        
        if not text:
            return {"error": "No text provided"}
        
        logger.info(f"Processing text: {text} (lang: {language})")
        
        # Step 1: Generate chatbot response
        response_text, emotion = chatbot_engine.generate_response(text)
        logger.info(f"Chatbot response: {response_text} (emotion: {emotion})")
        
        # Step 2: Generate speech and phonemes
        audio_path, phoneme_timeline = tts_engine.generate_speech_with_phonemes(
            response_text, language
        )
        
        if not audio_path:
            return {"error": "Failed to generate speech"}
        
        # Step 3: Generate viseme timeline
        viseme_timeline = lipsync_processor.phonemes_to_visemes(phoneme_timeline)
        smoothed_timeline = lipsync_processor.smooth_viseme_transitions(viseme_timeline)
        
        # Step 4: Create animation data
        animation_data = lipsync_processor.create_keyframe_animation(smoothed_timeline)
        
        # Step 5: Encode audio file as base64
        with open(audio_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode()
        
        # Clean up temporary file
        os.unlink(audio_path)
        
        return {
            "success": True,
            "input_text": text,
            "response_text": response_text,
            "emotion": emotion,
            "language": language,
            "audio_base64": audio_base64,
            "phoneme_timeline": phoneme_timeline,
            "viseme_timeline": smoothed_timeline,
            "animation_data": animation_data,
            "duration": animation_data["duration"]
        }
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return {"error": str(e)}


@app.post("/api/process-audio")
async def process_audio(audio_file: UploadFile = File(...)):
    """
    Process audio input through the complete pipeline.
    
    Args:
        audio_file: Uploaded WAV audio file
    
    Returns:
        Complete response with transcription and avatar response
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_audio_path = tmp_file.name
        
        logger.info(f"Processing uploaded audio: {audio_file.filename}")
        
        # Step 1: Speech-to-Text
        transcribed_text = stt_engine.recognize_from_file(tmp_audio_path)
        logger.info(f"Transcribed: {transcribed_text}")
        
        # Clean up uploaded file
        os.unlink(tmp_audio_path)
        
        if not transcribed_text:
            return {"error": "Could not transcribe audio"}
        
        # Step 2: Process through text pipeline
        language = chatbot_engine.detect_language(transcribed_text)
        text_response = await process_text({
            "text": transcribed_text,
            "language": language
        })
        
        # Add transcription to response
        if text_response.get("success"):
            text_response["transcribed_text"] = transcribed_text
        
        return text_response
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return {"error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    Supports streaming audio and real-time responses.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "text_input":
                # Process text input
                text = message.get("text", "")
                language = message.get("language", "en")
                
                # Send processing status
                await manager.send_personal_message(
                    json.dumps({"type": "status", "message": "Processing..."}),
                    websocket
                )
                
                # Process through pipeline
                result = await process_text({"text": text, "language": language})
                
                # Send result
                await manager.send_personal_message(
                    json.dumps({
                        "type": "response",
                        "data": result
                    }),
                    websocket
                )
            
            elif message["type"] == "audio_chunk":
                # Handle streaming audio (future implementation)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "status",
                        "message": "Streaming audio not yet implemented"
                    }),
                    websocket
                )
            
            elif message["type"] == "ping":
                # Heartbeat
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.get("/api/viseme-info")
async def get_viseme_info():
    """Get information about available visemes and their parameters."""
    if not lipsync_processor:
        return {"error": "Lip-sync processor not initialized"}
    
    return {
        "viseme_descriptions": lipsync_processor.viseme_descriptions,
        "phoneme_to_viseme_mapping": lipsync_processor.phoneme_to_viseme
    }


@app.get("/api/demo-animation")
async def get_demo_animation():
    """Get a demo animation for testing the 3D avatar."""
    try:
        # Create a demo sentence
        demo_text = "Hello! Welcome to the 3D Talking Avatar system!"
        
        # Generate demo animation
        result = await process_text({
            "text": demo_text,
            "language": "en"
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating demo: {e}")
        return {"error": str(e)}


# Serve static files (for CSS, JS, models, etc.)
@app.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """Serve static files."""
    static_path = f"static/{file_path}"
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return {"error": "File not found"}


def create_static_directory():
    """Create static directory for assets."""
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/models", exist_ok=True)
    os.makedirs("static/audio", exist_ok=True)


if __name__ == "__main__":
    # Create necessary directories
    create_static_directory()
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )