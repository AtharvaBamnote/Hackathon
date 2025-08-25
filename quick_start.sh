#!/bin/bash

# 🚀 3D Talking Avatar - Quick Start Script
# This script helps you get the system running quickly for hackathons

echo "🗣️ 3D Talking Avatar - Quick Start Setup"
echo "========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install basic requirements
echo "📥 Installing basic requirements..."
pip install --upgrade pip

# Install minimal requirements for demo
echo "Installing core dependencies..."
pip install fastapi uvicorn websockets python-multipart

# Create models directory
echo "📁 Creating directories..."
mkdir -p models
mkdir -p static/models
mkdir -p static/audio

# Download a small Vosk model for demo
echo "📡 Checking for Vosk model..."
if [ ! -d "models/vosk-model-en-us-0.22" ]; then
    echo "📥 Downloading English speech model (this may take a few minutes)..."
    echo "Model size: ~50MB"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd models
        wget -O vosk-model-en-us-0.22.zip https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
        unzip -q vosk-model-en-us-0.22.zip
        rm vosk-model-en-us-0.22.zip
        cd ..
        echo "✅ English model downloaded!"
    else
        echo "⚠️  Skipping model download. Speech recognition won't work without models."
    fi
else
    echo "✅ English model already exists!"
fi

# Test the standalone demo
echo "🧪 Testing standalone demo..."
python3 demo_standalone.py

# Check if full dependencies should be installed
echo ""
echo "🤔 Install full dependencies for complete functionality?"
echo "This includes TTS, STT, and audio processing libraries."
echo "Size: ~500MB+ (includes ML models)"
read -p "Install full dependencies? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Installing full requirements..."
    pip install -r requirements_avatar.txt
    echo "✅ Full installation complete!"
    
    echo "🚀 Starting the server..."
    echo "The server will start on http://localhost:8000"
    echo "Press Ctrl+C to stop the server when done."
    echo ""
    python3 server.py
else
    echo "⚠️  Minimal installation complete."
    echo ""
    echo "📋 Next steps:"
    echo "1. Install full dependencies: pip install -r requirements_avatar.txt"
    echo "2. Start the server: python3 server.py"
    echo "3. Open browser: http://localhost:8000"
    echo ""
    echo "🧪 For now, you can test the demo with:"
    echo "python3 demo_standalone.py"
fi

echo ""
echo "🎉 Setup complete! Happy hacking!"