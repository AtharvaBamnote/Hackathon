#!/usr/bin/env python3
"""
Test Script for Vehicle Detection System
========================================

This script demonstrates how to use the Vehicle Detection System
with various input types and configurations.

Usage Examples:
- Process single image: python test_vehicle_detection.py
- Process with custom confidence: python test_vehicle_detection.py --confidence 0.7
- Process batch of images: python test_vehicle_detection.py --batch
"""

import os
import sys
import urllib.request
from pathlib import Path
import cv2
import numpy as np
from vehicle_detection_system import VehicleDetectionSystem
import argparse

def download_sample_images():
    """Download sample traffic images for testing."""
    sample_dir = Path("sample_images")
    sample_dir.mkdir(exist_ok=True)
    
    # Sample traffic images (using publicly available images)
    sample_urls = [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop",  # Traffic
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&h=600&fit=crop",  # Highway
        "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=800&h=600&fit=crop",  # City traffic
    ]
    
    downloaded_files = []
    
    for i, url in enumerate(sample_urls):
        filename = sample_dir / f"traffic_sample_{i+1}.jpg"
        
        if not filename.exists():
            try:
                print(f"Downloading sample image {i+1}...")
                urllib.request.urlretrieve(url, filename)
                downloaded_files.append(filename)
            except Exception as e:
                print(f"Failed to download {url}: {e}")
        else:
            downloaded_files.append(filename)
    
    return downloaded_files

def create_synthetic_test_image():
    """Create a synthetic test image with drawn vehicles for testing."""
    # Create a 800x600 image
    img = np.ones((600, 800, 3), dtype=np.uint8) * 50  # Dark gray background
    
    # Draw a road
    cv2.rectangle(img, (0, 300), (800, 500), (70, 70, 70), -1)
    
    # Draw lane lines
    for x in range(0, 800, 50):
        cv2.rectangle(img, (x, 395), (x+25, 405), (255, 255, 255), -1)
    
    # Draw some simple car shapes
    # Car 1 (red)
    cv2.rectangle(img, (100, 350), (180, 400), (0, 0, 200), -1)
    cv2.rectangle(img, (110, 330), (170, 350), (100, 100, 255), -1)
    cv2.circle(img, (120, 400), 15, (0, 0, 0), -1)  # Wheel
    cv2.circle(img, (160, 400), 15, (0, 0, 0), -1)  # Wheel
    
    # Car 2 (blue)
    cv2.rectangle(img, (300, 360), (380, 410), (200, 100, 0), -1)
    cv2.rectangle(img, (310, 340), (370, 360), (255, 150, 100), -1)
    cv2.circle(img, (320, 410), 15, (0, 0, 0), -1)  # Wheel
    cv2.circle(img, (360, 410), 15, (0, 0, 0), -1)  # Wheel
    
    # Truck (green)
    cv2.rectangle(img, (500, 340), (620, 420), (0, 150, 0), -1)
    cv2.rectangle(img, (510, 310), (570, 340), (0, 200, 0), -1)
    cv2.circle(img, (520, 420), 20, (0, 0, 0), -1)  # Wheel
    cv2.circle(img, (600, 420), 20, (0, 0, 0), -1)  # Wheel
    
    # Add some buildings in background
    cv2.rectangle(img, (50, 50), (150, 200), (100, 100, 100), -1)
    cv2.rectangle(img, (200, 80), (300, 220), (80, 80, 80), -1)
    cv2.rectangle(img, (650, 60), (750, 180), (90, 90, 90), -1)
    
    return img

def test_single_image(detector, image_path):
    """Test detection on a single image."""
    print(f"\n{'='*50}")
    print("TESTING SINGLE IMAGE DETECTION")
    print(f"{'='*50}")
    
    try:
        result = detector.process_image(image_path)
        
        print(f"✅ Successfully processed: {image_path}")
        print(f"📊 Total vehicles detected: {result['total_vehicles']}")
        
        for vehicle_type, count in result['vehicle_counts'].items():
            if count > 0:
                print(f"   {vehicle_type.title()}s: {count}")
        
        if 'output_path' in result:
            print(f"💾 Result saved to: {result['output_path']}")
            
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")

def test_batch_processing(detector, image_directory):
    """Test batch processing of multiple images."""
    print(f"\n{'='*50}")
    print("TESTING BATCH PROCESSING")
    print(f"{'='*50}")
    
    try:
        results = detector.process_batch(image_directory)
        
        if results:
            print(f"✅ Successfully processed {len(results)} images")
            total_vehicles = sum(r['total_vehicles'] for r in results)
            print(f"📊 Total vehicles across all images: {total_vehicles}")
        else:
            print("❌ No images processed successfully")
            
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")

def test_confidence_threshold(detector, image_path):
    """Test different confidence thresholds."""
    print(f"\n{'='*50}")
    print("TESTING DIFFERENT CONFIDENCE THRESHOLDS")
    print(f"{'='*50}")
    
    thresholds = [0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        detector.confidence_threshold = threshold
        
        try:
            result = detector.process_image(image_path, save_result=False)
            print(f"Confidence {threshold}: {result['total_vehicles']} vehicles detected")
            
        except Exception as e:
            print(f"Error with confidence {threshold}: {e}")

def create_demo_scene():
    """Create a demo scene with synthetic vehicles for testing."""
    demo_dir = Path("demo_images")
    demo_dir.mkdir(exist_ok=True)
    
    # Create synthetic test image
    synthetic_img = create_synthetic_test_image()
    demo_path = demo_dir / "synthetic_traffic.jpg"
    cv2.imwrite(str(demo_path), synthetic_img)
    
    print(f"📸 Created synthetic test image: {demo_path}")
    return demo_path

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test Vehicle Detection System")
    parser.add_argument("--confidence", "-c", type=float, default=0.5,
                       help="Confidence threshold for testing")
    parser.add_argument("--model", "-m", default="yolov8n.pt",
                       help="YOLOv8 model to use")
    parser.add_argument("--batch", "-b", action="store_true",
                       help="Test batch processing")
    parser.add_argument("--download", "-d", action="store_true",
                       help="Download sample images")
    parser.add_argument("--synthetic", "-s", action="store_true",
                       help="Test with synthetic image")
    
    args = parser.parse_args()
    
    print("🚗 Vehicle Detection System - Test Suite")
    print("="*50)
    
    # Initialize detection system
    try:
        detector = VehicleDetectionSystem(
            model_path=args.model,
            confidence_threshold=args.confidence
        )
        print("✅ Detection system initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize detection system: {e}")
        return 1
    
    # Create synthetic test image if requested
    if args.synthetic:
        demo_path = create_demo_scene()
        test_single_image(detector, str(demo_path))
    
    # Download and test sample images if requested
    if args.download:
        try:
            sample_files = download_sample_images()
            if sample_files:
                print(f"✅ Downloaded {len(sample_files)} sample images")
                
                # Test single image
                test_single_image(detector, str(sample_files[0]))
                
                # Test batch processing if requested
                if args.batch:
                    test_batch_processing(detector, "sample_images")
                    
        except Exception as e:
            print(f"❌ Error downloading samples: {e}")
    
    # Test confidence thresholds if we have images
    sample_dir = Path("sample_images")
    demo_dir = Path("demo_images")
    
    test_image = None
    if sample_dir.exists() and list(sample_dir.glob("*.jpg")):
        test_image = str(list(sample_dir.glob("*.jpg"))[0])
    elif demo_dir.exists() and list(demo_dir.glob("*.jpg")):
        test_image = str(list(demo_dir.glob("*.jpg"))[0])
    
    if test_image:
        test_confidence_threshold(detector, test_image)
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"🎯 Total detections made: {detector.total_detections}")
    
    for vehicle_type, count in detector.detection_counts.items():
        if count > 0:
            print(f"   {vehicle_type.title()}s detected: {count}")
    
    print("\n📁 Check the 'detection_results' directory for output images")
    print("✨ Test suite completed!")
    
    return 0

if __name__ == "__main__":
    exit(main())