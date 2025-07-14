# 🐅 Tiger Detection Dashboard

A modern web-based tiger surveillance and object detection system using YOLOv8 and FastAPI.

## Features

- 📹 **Multiple Camera Feeds**: Support for up to 4 camera feeds
- 🔍 **Real-time Detection**: AI-powered tiger and object detection using YOLOv8
- 📤 **Image Upload**: Upload and analyze custom images
- 💻 **Modern Web Interface**: Beautiful, responsive dashboard
- 📊 **Detection Results**: Detailed results with confidence scores and bounding boxes

## Quick Start

### Option 1: Run the Startup Script (Recommended)
```bash
python run_server.py
```

### Option 2: Manual Setup
1. Install dependencies:
```bash
pip install -r tiger_requirements.txt
```

2. Run the backend server:
```bash
python backend.py
```

### Option 3: Using Uvicorn directly
```bash
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

## Access the Dashboard

Once the server is running, open your web browser and go to:
- **Frontend Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Project Structure

```
tiger-detection/
├── backend.py                 # FastAPI backend server
├── run_server.py             # Startup script
├── tiger_requirements.txt    # Project dependencies
├── frontend/
│   ├── TigerDetectionUI.html # Main dashboard interface
│   ├── cam-feed/            # Camera feed images
│   │   ├── cam1.jpg
│   │   ├── cam2.jpg
│   │   ├── cam3.jpg
│   │   └── cam4.jpg
│   └── thumbs/              # Thumbnail images
│       ├── cam1.jpg
│       ├── cam2.jpg
│       ├── cam3.jpg
│       └── cam4.jpg
└── best.pt                  # Your trained YOLO model (optional)
```

## How to Use

### Camera Feed Detection
1. Click on any camera button (Camera 1-4)
2. The camera feed will load in the display area
3. Click "🔍 Detect Tigers" to analyze the image
4. View results in the Detection Results section

### Upload & Analyze
1. Click "Choose Image" to upload a custom image
2. The image will appear in the upload display area
3. Click "🔍 Analyze Image" to detect objects
4. View results in the Detection Results section

## Model Information

- **Default Model**: YOLOv8n (downloads automatically if `best.pt` not found)
- **Custom Model**: Place your trained `best.pt` file in the project root
- **Confidence Threshold**: 0.4 (40%)
- **Supported Formats**: JPG, PNG, and other common image formats

## API Endpoints

- `GET /` - Serve the main dashboard
- `GET /cam-feed/{camera_id}` - Get camera feed image
- `GET /thumbs/{camera_id}` - Get camera thumbnail
- `GET /predict/{camera_id}` - Run detection on camera feed
- `POST /upload-and-predict` - Upload and analyze custom image
- `GET /docs` - API documentation

## Dependencies

- **FastAPI**: Web framework for the API
- **Uvicorn**: ASGI server
- **Ultralytics**: YOLOv8 implementation
- **OpenCV**: Image processing
- **Python-multipart**: File upload support

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r tiger_requirements.txt
   ```

2. **"best.pt not found"**
   - The system will automatically use YOLOv8n
   - Place your custom model file in the project root if available

3. **"Camera feed not available"**
   - Sample images will be created automatically
   - Replace images in `frontend/cam-feed/` with your actual camera feeds

4. **Port already in use**
   - Change the port in `backend.py` or `run_server.py`
   - Or stop other services using port 8000

### Performance Tips

- Use GPU acceleration if available (CUDA)
- Optimize image sizes for faster processing
- Adjust confidence threshold based on your needs

## Development

To modify the detection confidence or add new features:

1. Edit `backend.py` for API changes
2. Edit `frontend/TigerDetectionUI.html` for UI changes
3. Restart the server to see changes

## Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Ensure Python 3.8+ is being used
3. Verify that the required directories exist
4. Check the console for error messages

---

**Happy Tiger Spotting! 🐅**