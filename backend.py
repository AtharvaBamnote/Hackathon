from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import shutil
import os

app = FastAPI(title="Tiger Surveillance Dashboard")

# Add CORS middleware to allow frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
Path("frontend").mkdir(exist_ok=True)
Path("frontend/cam-feed").mkdir(exist_ok=True)
Path("frontend/thumbs").mkdir(exist_ok=True)

# Mount static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Load YOLOv8 model (we'll use a pre-trained model if best.pt doesn't exist)
try:
    model = YOLO("best.pt")
except:
    print("best.pt not found, using yolov8n.pt instead")
    model = YOLO("yolov8n.pt")  # This will download automatically if not present

# Serve index.html
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = Path("frontend/TigerDetectionUI.html")
    if html_path.exists():
        return html_path.read_text()
    else:
        return """
        <html>
        <body>
        <h1>Tiger Detection Dashboard</h1>
        <p>Frontend file not found. Please check if TigerDetectionUI.html exists in the frontend directory.</p>
        </body>
        </html>
        """

# Endpoint for serving live camera feed (simulated as image)
@app.get("/cam-feed/{camera_id}", response_class=FileResponse)
async def get_cam_feed(camera_id: str):
    image_path = Path(f"frontend/cam-feed/{camera_id}.jpg")
    if image_path.exists():
        return FileResponse(image_path)
    return JSONResponse(content={"error": "Feed not found"}, status_code=404)

# Endpoint for thumbnails
@app.get("/thumbs/{camera_id}", response_class=FileResponse)
async def get_thumbnail(camera_id: str):
    image_path = Path(f"frontend/thumbs/{camera_id}.jpg")
    if image_path.exists():
        return FileResponse(image_path)
    return JSONResponse(content={"error": "Thumbnail not found"}, status_code=404)

# 🔍 Detection endpoint
@app.get("/predict/{camera_id}")
async def predict_tiger_from_cam(camera_id: str):
    img_path = Path(f"frontend/cam-feed/{camera_id}.jpg")
    if not img_path.exists():
        return JSONResponse(content={"error": "Image not found"}, status_code=404)

    # Run inference
    results = model.predict(source=str(img_path), conf=0.4)

    detection_list = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                detection_list.append({
                    "class": model.names[cls_id],
                    "confidence": round(conf, 3),
                    "bbox": [round(coord, 1) for coord in xyxy]
                })

    return {"camera_id": camera_id, "detections": detection_list}

# 📤 Optional: Upload and predict on custom image
@app.post("/upload-and-predict")
async def upload_and_predict(file: UploadFile = File(...)):
    temp_path = Path(f"temp_{file.filename}")
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = model.predict(source=str(temp_path), conf=0.4)

    detection_list = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                detection_list.append({
                    "class": model.names[cls_id],
                    "confidence": round(conf, 3),
                    "bbox": [round(coord, 1) for coord in xyxy]
                })

    temp_path.unlink()  # Clean up
    return {"filename": file.filename, "detections": detection_list}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)