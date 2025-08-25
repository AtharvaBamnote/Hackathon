"""
Speech-to-Text module using Vosk for offline recognition.
Supports English and Hindi languages.
"""

import json
import wave
import pyaudio
import vosk
import threading
import queue
import os
from typing import Optional, Callable


class SpeechToText:
    def __init__(self, model_path: str = None, lang: str = "en"):
        """
        Initialize STT with Vosk model.
        
        Args:
            model_path: Path to Vosk model directory
            lang: Language code ('en' for English, 'hi' for Hindi)
        """
        self.lang = lang
        self.model = None
        self.rec = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Default model paths (download these models first)
        if model_path is None:
            if lang == "en":
                model_path = "models/vosk-model-en-us-0.22"
            elif lang == "hi":
                model_path = "models/vosk-model-hi-0.22"
            else:
                model_path = "models/vosk-model-en-us-0.22"
        
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Load the Vosk model."""
        try:
            if os.path.exists(self.model_path):
                self.model = vosk.Model(self.model_path)
                self.rec = vosk.KaldiRecognizer(self.model, 16000)
                self.rec.SetWords(True)
                print(f"Loaded Vosk model from {self.model_path}")
            else:
                print(f"Model not found at {self.model_path}")
                print("Please download Vosk models:")
                print("English: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
                print("Hindi: https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def recognize_from_file(self, audio_file: str) -> str:
        """
        Recognize speech from audio file.
        
        Args:
            audio_file: Path to WAV audio file
            
        Returns:
            Recognized text
        """
        if not self.model:
            return "Model not loaded"
        
        try:
            wf = wave.open(audio_file, 'rb')
            
            # Check audio format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                print("Audio file must be WAV format mono PCM 16kHz")
                return ""
            
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                    
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    if result.get('text'):
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(self.rec.FinalResult())
            if final_result.get('text'):
                results.append(final_result['text'])
            
            wf.close()
            return ' '.join(results)
            
        except Exception as e:
            print(f"Error recognizing audio: {e}")
            return ""
    
    def start_listening(self, callback: Callable[[str], None]):
        """
        Start real-time listening from microphone.
        
        Args:
            callback: Function to call with recognized text
        """
        if not self.model:
            print("Model not loaded")
            return
        
        self.is_listening = True
        self.callback = callback
        
        # Start audio capture thread
        audio_thread = threading.Thread(target=self._capture_audio)
        audio_thread.daemon = True
        audio_thread.start()
        
        # Start recognition thread
        recognition_thread = threading.Thread(target=self._process_audio)
        recognition_thread.daemon = True
        recognition_thread.start()
    
    def stop_listening(self):
        """Stop listening."""
        self.is_listening = False
    
    def _capture_audio(self):
        """Capture audio from microphone."""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000
            )
            
            print("Listening... (Press Ctrl+C to stop)")
            
            while self.is_listening:
                data = stream.read(4000, exception_on_overflow=False)
                self.audio_queue.put(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Error capturing audio: {e}")
    
    def _process_audio(self):
        """Process captured audio for recognition."""
        try:
            while self.is_listening:
                if not self.audio_queue.empty():
                    data = self.audio_queue.get()
                    
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get('text', '').strip()
                        if text and self.callback:
                            self.callback(text)
                    
        except Exception as e:
            print(f"Error processing audio: {e}")


def test_stt():
    """Test function for STT."""
    stt = SpeechToText(lang="en")
    
    def on_speech(text):
        print(f"Recognized: {text}")
    
    # Test with microphone (uncomment to test)
    # stt.start_listening(on_speech)
    # import time
    # time.sleep(10)
    # stt.stop_listening()
    
    print("STT module ready!")


if __name__ == "__main__":
    test_stt()