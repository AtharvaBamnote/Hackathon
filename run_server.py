#!/usr/bin/env python3
"""
Tiger Detection Dashboard Startup Script
Run this file to start the Tiger Detection Dashboard server.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'ultralytics',
        'opencv-python',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    print("✅ All dependencies are installed")
    return True

def create_sample_images():
    """Create sample placeholder images for testing"""
    try:
        import cv2
        import numpy as np
        
        # Create sample images for camera feeds
        for i in range(1, 5):
            # Create a simple colored image with text
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Different colors for different cameras
            colors = [(100, 50, 150), (50, 150, 100), (150, 100, 50), (100, 100, 150)]
            img[:] = colors[i-1]
            
            # Add text
            cv2.putText(img, f'Camera {i} Feed', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(img, 'Sample Image for Testing', (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Save camera feed
            cv2.imwrite(f'frontend/cam-feed/cam{i}.jpg', img)
            
            # Create thumbnail (smaller version)
            thumb = cv2.resize(img, (160, 120))
            cv2.imwrite(f'frontend/thumbs/cam{i}.jpg', thumb)
        
        print("✅ Sample camera images created")
        
    except ImportError:
        print("⚠️  OpenCV not available, skipping sample image creation")
    except Exception as e:
        print(f"⚠️  Error creating sample images: {e}")

def main():
    """Main function to start the server"""
    print("🐅 Tiger Detection Dashboard - Starting Server...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies. Please install them manually.")
        return
    
    # Create sample images
    create_sample_images()
    
    # Start the server
    print("\n🚀 Starting FastAPI server...")
    print("📱 Frontend will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("\n⚡ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the backend
        from backend import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Please check if backend.py exists and is properly configured")

if __name__ == "__main__":
    main()