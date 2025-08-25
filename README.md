# 🗣️ 3D Talking Avatar System

A hackathon-ready multilingual 3D talking avatar system that converts speech to animated avatar responses with real-time lip-sync. Built with Python backend and Three.js frontend.

## 🚀 Features

- **Multilingual Support**: English and Hindi speech recognition and synthesis
- **Offline Operation**: No paid APIs or cloud dependencies
- **Real-time Lip-sync**: Phoneme-to-viseme mapping for natural mouth movements
- **Emotion Detection**: Facial expressions based on conversation sentiment
- **Web Interface**: Modern Three.js-based 3D avatar renderer
- **Modular Architecture**: Clean, extensible codebase

## 🏗️ System Architecture

```
User Input (Speech/Text) 
    ↓
[STT Module] → [Chatbot] → [TTS Module] → [Lip-sync] → [3D Avatar]
    ↓              ↓           ↓            ↓           ↓
  Vosk         Rule-based   Coqui TTS   Viseme Map   Three.js
```

## 📋 Requirements

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install ffmpeg

# macOS
brew install espeak portaudio
brew install ffmpeg
```

### Python Dependencies
```bash
pip install -r requirements_avatar.txt
```

## 🛠️ Installation

### Step 1: Clone and Setup
```bash
git clone <your-repo>
cd 3d-talking-avatar
pip install -r requirements_avatar.txt
```

### Step 2: Download Vosk Models
```bash
# Create models directory
mkdir -p models

# Download English model (Recommended: ~50MB)
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip -d models/

# Download Hindi model (Optional: ~180MB)
wget https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip
unzip vosk-model-hi-0.22.zip -d models/
```

### Step 3: Test Individual Components
```bash
# Test Speech-to-Text
python stt.py

# Test Chatbot
python chatbot.py

# Test Text-to-Speech
python tts.py

# Test Lip-sync
python lip_sync.py
```

### Step 4: Run the Server
```bash
python server.py
```

### Step 5: Open in Browser
Navigate to: `http://localhost:8000`

## 📁 Project Structure

```
3d-talking-avatar/
├── stt.py                 # Speech-to-Text using Vosk
├── chatbot.py             # Multilingual NLP engine
├── tts.py                 # Text-to-Speech with Coqui TTS
├── lip_sync.py            # Phoneme to viseme mapping
├── server.py              # FastAPI backend server
├── frontend.html          # Three.js web interface
├── requirements_avatar.txt # Python dependencies
├── README.md              # This file
├── models/                # Vosk speech models
│   ├── vosk-model-en-us-0.22/
│   └── vosk-model-hi-0.22/
└── static/                # Static assets (auto-created)
    ├── models/            # 3D avatar models
    └── audio/             # Generated audio files
```

## 🎯 Component Details

### 1. Speech-to-Text (`stt.py`)
- **Engine**: Vosk (offline)
- **Languages**: English, Hindi
- **Features**: Real-time and file-based recognition
- **Models**: Lightweight models for fast processing

### 2. Chatbot (`chatbot.py`)
- **Type**: Rule-based multilingual system
- **Features**: Intent detection, emotion analysis
- **Languages**: English and Hindi responses
- **Extensible**: Easy to add more languages/intents

### 3. Text-to-Speech (`tts.py`)
- **Engine**: Coqui TTS
- **Features**: Multilingual synthesis, phoneme extraction
- **Fallback**: System TTS if Coqui fails
- **Output**: WAV audio + phoneme timeline

### 4. Lip-sync (`lip_sync.py`)
- **Input**: Phoneme timeline from TTS
- **Output**: Viseme timeline for animation
- **Features**: 14 viseme types, smoothing, keyframe export
- **Formats**: Three.js and Unity compatible

### 5. Backend Server (`server.py`)
- **Framework**: FastAPI
- **Features**: REST API, WebSocket support
- **Endpoints**: Text processing, audio upload, demo
- **Pipeline**: Complete STT → NLP → TTS → Lip-sync

### 6. Frontend (`frontend.html`)
- **Framework**: Three.js
- **Features**: 3D avatar, real-time animation
- **UI**: Modern responsive design
- **Inputs**: Text, voice recording, file upload

## 🎮 Usage Examples

### Text Input
```python
# Send POST request to /api/process-text
{
    "text": "Hello! How are you today?",
    "language": "en"
}

# Response includes:
{
    "success": true,
    "response_text": "I'm doing great, thank you for asking! How are you?",
    "emotion": "happy",
    "audio_base64": "...",
    "viseme_timeline": [...],
    "animation_data": {...}
}
```

### Voice Input
```python
# Upload WAV file to /api/process-audio
# Returns transcription + complete response
```

### Viseme Timeline Format
```json
[
    {
        "time": 0.0,
        "viseme": "H",
        "duration": 0.1,
        "parameters": {
            "mouth_open": 0.3,
            "mouth_width": 0.6,
            "lip_pucker": 0.0
        },
        "description": "Glottal fricative",
        "original_phoneme": "h"
    }
]
```

## 🎨 3D Avatar Integration

### Three.js Integration
```javascript
// Load viseme timeline
function animateVisemes(visemeTimeline) {
    visemeTimeline.forEach((viseme, index) => {
        setTimeout(() => {
            // Apply mouth shape parameters
            avatar.morphTargetInfluences[0] = viseme.parameters.mouth_open;
            avatar.morphTargetInfluences[1] = viseme.parameters.mouth_width;
            avatar.morphTargetInfluences[2] = viseme.parameters.lip_pucker;
        }, viseme.time * 1000);
    });
}
```

### Unity Integration
```csharp
// Use the exported animation data
public class LipSyncAnimator : MonoBehaviour {
    public void PlayLipSync(string animationJson) {
        var data = JsonUtility.FromJson<LipSyncData>(animationJson);
        // Apply curves to facial blend shapes
    }
}
```

## 🔧 Customization

### Adding New Languages
1. Add language mappings in `chatbot.py`
2. Update TTS language codes in `tts.py`
3. Download appropriate Vosk models
4. Add phoneme mappings in `lip_sync.py`

### Custom Avatar Models
1. Place GLTF/FBX models in `static/models/`
2. Update frontend.html to load your model
3. Map viseme parameters to your model's blend shapes

### Extending Emotions
1. Add emotion keywords in `chatbot.py`
2. Create corresponding facial expressions
3. Update animation mapping in frontend

## 🐛 Troubleshooting

### Common Issues

**1. Vosk Model Not Found**
```bash
# Download the models to the correct directory
mkdir -p models
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip -d models/
```

**2. Audio Recording Not Working**
```bash
# Install audio dependencies
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**3. TTS Model Loading Slow**
```bash
# First run downloads models (can take time)
# Subsequent runs will be faster
# Use smaller models for faster loading
```

**4. Frontend Not Loading**
```bash
# Check if server is running on port 8000
python server.py
# Navigate to http://localhost:8000
```

## 🚀 Performance Optimization

### For Hackathons
1. Use smaller Vosk models for faster loading
2. Pre-download TTS models before demo
3. Test on target hardware beforehand
4. Have fallback responses ready

### Production Deployment
1. Use GPU for TTS if available
2. Implement audio streaming for real-time
3. Add caching for common responses
4. Optimize 3D models for web

## 📊 Benchmark Results

**Typical Processing Times:**
- STT (Vosk): ~0.5-1.5s for 5s audio
- Chatbot: ~0.1s response generation
- TTS (Coqui): ~1-3s for short sentences
- Lip-sync: ~0.1s timeline generation
- **Total Pipeline**: ~2-5s end-to-end

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new components
4. Submit pull request

## 📄 License

MIT License - feel free to use for hackathons and projects!

## 🙏 Acknowledgments

- **Vosk**: Offline speech recognition
- **Coqui TTS**: Neural text-to-speech
- **Three.js**: 3D web graphics
- **FastAPI**: Modern Python web framework

## 📞 Support

For hackathon support or questions:
- Check the troubleshooting section
- Test individual components first
- Ensure all dependencies are installed
- Use provided demo endpoints for testing

---

**Happy Hacking! 🚀** Built for hackathons with ❤️