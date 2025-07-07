# Vehicle Detection System

Computer Vision System for Traffic Analysis

## Overview

This project is a comprehensive computer vision system that automatically detects, classifies, and counts vehicles in traffic images. The system uses YOLOv8 (You Only Look Once) deep learning model to identify cars, trucks, motorcycles, and buses with high accuracy, providing visual feedback through bounding boxes and confidence scores.

## Features

- **Vehicle Detection**: Identify vehicles in images using state-of-the-art bounding boxes
- **Multi-Class Classification**: Categorize vehicles into cars, trucks, motorcycles, and buses
- **Confidence Scoring**: Display confidence levels for each detection
- **Vehicle Counting**: Count total vehicles by type with detailed statistics
- **Visual Output**: Save processed images with clean annotations
- **Batch Processing**: Process multiple images in directories
- **Video Support**: Real-time processing of video files
- **Comprehensive Reporting**: Generate detailed JSON reports with statistics

## Technologies Used

- **Python 3.8+**: Core programming language
- **YOLOv8 (Ultralytics)**: State-of-the-art object detection model
- **OpenCV**: Computer vision and image processing
- **PyTorch**: Deep learning framework
- **NumPy**: Scientific computing
- **Matplotlib**: Visualization and plotting

## Installation & Setup

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/vehicle-detection-system.git
cd vehicle-detection-system
```

### 2. Install dependencies:
```bash
# Option 1: Use the focused requirements file
pip install -r vehicle_detection_requirements.txt

# Option 2: Install core packages manually
pip install ultralytics opencv-python torch torchvision numpy matplotlib
```

### 3. Verify installation:
```bash
python test_vehicle_detection.py --synthetic
```

## Quick Start

### Process a single image:
```bash
python vehicle_detection_system.py --input path/to/image.jpg
```

### Process multiple images:
```bash
python vehicle_detection_system.py --input path/to/directory --batch
```

### Process video:
```bash
python vehicle_detection_system.py --input video.mp4 --video --output detected_video.mp4
```

### Custom confidence threshold:
```bash
python vehicle_detection_system.py --input image.jpg --confidence 0.7
```

## Usage Examples

### Python API Usage:
```python
from vehicle_detection_system import VehicleDetectionSystem

# Initialize detector
detector = VehicleDetectionSystem(confidence_threshold=0.5)

# Process single image
result = detector.process_image("traffic_image.jpg")
print(f"Detected {result['total_vehicles']} vehicles")

# Process batch
results = detector.process_batch("images_directory/")
```

### Test Suite:
```bash
# Run comprehensive tests
python test_vehicle_detection.py --download --batch --synthetic

# Test with different confidence levels
python test_vehicle_detection.py --confidence 0.7 --synthetic
```

## Output

The system produces:
- **Annotated Images**: Original images with bounding boxes, labels, and confidence scores
- **Summary Statistics**: Vehicle counts by type displayed on images
- **JSON Reports**: Detailed detection results and statistics
- **Batch Reports**: Comprehensive analysis for multiple images

## Supported Vehicle Types

- 🚗 **Cars**: Standard passenger vehicles
- 🏍️ **Motorcycles**: Two-wheeled motor vehicles  
- 🚛 **Trucks**: Commercial and freight vehicles
- 🚌 **Buses**: Public transportation vehicles

## Model Information

- **Base Model**: YOLOv8 (nano version for speed, other variants available)
- **Pre-trained**: Uses COCO dataset vehicle classes
- **No Training Required**: Ready to use out of the box
- **GPU Acceleration**: Automatically uses CUDA if available

## Directory Structure

```
vehicle-detection-system/
├── vehicle_detection_system.py    # Main detection system
├── test_vehicle_detection.py      # Test suite and examples
├── vehicle_detection_requirements.txt  # Minimal requirements
├── requirements.txt               # Full environment requirements
├── README.md                      # This file
├── detection_results/             # Output directory (created automatically)
├── sample_images/                 # Downloaded test images
└── demo_images/                   # Synthetic test images
```

## Performance Notes

- **Speed**: ~50-100ms per image on GPU, ~200-500ms on CPU
- **Accuracy**: High precision with YOLOv8 pre-trained weights
- **Memory**: ~1-2GB GPU memory for inference
- **Formats**: Supports JPG, PNG, BMP, TIFF image formats

## Current Status

✅ **Core Features Complete**:
- Single image processing
- Batch processing
- Video processing
- Confidence thresholding
- Multiple output formats
- Comprehensive documentation

🚀 **Ready for Production Use**

## Contributing

Contributions and feedback are welcome! Please feel free to submit issues, feature requests, or pull requests.

