#!/usr/bin/env python3
"""
Vehicle Detection System - Comprehensive Demo
=============================================

This script demonstrates all features of the Vehicle Detection System
including single image processing, batch processing, and various
confidence thresholds.

Usage:
    python demo.py

Features demonstrated:
- System initialization
- Synthetic image creation and testing
- Single image processing
- Batch processing
- Confidence threshold testing
- Performance benchmarking
- Results visualization
"""

import os
import time
import urllib.request
from pathlib import Path
import cv2
import numpy as np
from vehicle_detection_system import VehicleDetectionSystem

def create_demo_images():
    """Create demo images with different traffic scenarios."""
    demo_dir = Path("demo_images")
    demo_dir.mkdir(exist_ok=True)
    
    demo_images = []
    
    # Demo 1: Simple highway scene
    print("📸 Creating highway demo image...")
    highway_img = np.ones((480, 640, 3), dtype=np.uint8) * 135  # Gray background
    
    # Draw highway
    cv2.rectangle(highway_img, (0, 200), (640, 400), (80, 80, 80), -1)
    
    # Lane markings
    for x in range(0, 640, 40):
        cv2.rectangle(highway_img, (x, 295), (x+20, 305), (255, 255, 255), -1)
    
    # Cars
    # Red car
    cv2.rectangle(highway_img, (100, 250), (160, 300), (50, 50, 200), -1)
    cv2.rectangle(highway_img, (110, 230), (150, 250), (80, 80, 220), -1)
    cv2.circle(highway_img, (115, 300), 12, (0, 0, 0), -1)
    cv2.circle(highway_img, (145, 300), 12, (0, 0, 0), -1)
    
    # Blue car
    cv2.rectangle(highway_img, (250, 320), (310, 370), (200, 100, 50), -1)
    cv2.rectangle(highway_img, (260, 300), (300, 320), (220, 120, 70), -1)
    cv2.circle(highway_img, (265, 370), 12, (0, 0, 0), -1)
    cv2.circle(highway_img, (295, 370), 12, (0, 0, 0), -1)
    
    # Truck
    cv2.rectangle(highway_img, (400, 240), (500, 320), (100, 150, 100), -1)
    cv2.rectangle(highway_img, (410, 210), (460, 240), (120, 170, 120), -1)
    cv2.circle(highway_img, (420, 320), 15, (0, 0, 0), -1)
    cv2.circle(highway_img, (480, 320), 15, (0, 0, 0), -1)
    
    # Environment
    cv2.rectangle(highway_img, (50, 50), (120, 150), (100, 100, 100), -1)  # Building
    cv2.rectangle(highway_img, (500, 60), (580, 140), (90, 90, 90), -1)   # Building
    
    highway_path = demo_dir / "highway_scene.jpg"
    cv2.imwrite(str(highway_path), highway_img)
    demo_images.append(highway_path)
    
    # Demo 2: City intersection
    print("📸 Creating city intersection demo image...")
    city_img = np.ones((480, 640, 3), dtype=np.uint8) * 120
    
    # Roads
    cv2.rectangle(city_img, (0, 200), (640, 280), (70, 70, 70), -1)  # Horizontal road
    cv2.rectangle(city_img, (280, 0), (360, 480), (70, 70, 70), -1)  # Vertical road
    
    # Intersection
    cv2.rectangle(city_img, (280, 200), (360, 280), (60, 60, 60), -1)
    
    # Lane lines
    cv2.line(city_img, (0, 240), (280, 240), (255, 255, 255), 2)
    cv2.line(city_img, (360, 240), (640, 240), (255, 255, 255), 2)
    cv2.line(city_img, (320, 0), (320, 200), (255, 255, 255), 2)
    cv2.line(city_img, (320, 280), (320, 480), (255, 255, 255), 2)
    
    # Vehicles at intersection
    # Car 1 (waiting)
    cv2.rectangle(city_img, (200, 210), (250, 240), (0, 100, 200), -1)
    cv2.circle(city_img, (210, 240), 8, (0, 0, 0), -1)
    cv2.circle(city_img, (240, 240), 8, (0, 0, 0), -1)
    
    # Car 2 (crossing)
    cv2.rectangle(city_img, (290, 150), (320, 190), (200, 50, 0), -1)
    cv2.circle(city_img, (295, 190), 8, (0, 0, 0), -1)
    cv2.circle(city_img, (315, 190), 8, (0, 0, 0), -1)
    
    # Motorcycle
    cv2.rectangle(city_img, (450, 225), (470, 255), (0, 150, 100), -1)
    cv2.circle(city_img, (455, 255), 6, (0, 0, 0), -1)
    cv2.circle(city_img, (465, 255), 6, (0, 0, 0), -1)
    
    # Buildings
    cv2.rectangle(city_img, (50, 50), (200, 180), (80, 80, 80), -1)
    cv2.rectangle(city_img, (450, 60), (600, 170), (85, 85, 85), -1)
    cv2.rectangle(city_img, (100, 300), (250, 430), (75, 75, 75), -1)
    cv2.rectangle(city_img, (400, 320), (550, 450), (90, 90, 90), -1)
    
    city_path = demo_dir / "city_intersection.jpg"
    cv2.imwrite(str(city_path), city_img)
    demo_images.append(city_path)
    
    # Demo 3: Parking lot
    print("📸 Creating parking lot demo image...")
    parking_img = np.ones((480, 640, 3), dtype=np.uint8) * 150
    
    # Parking spaces
    for i in range(6):
        x = 50 + i * 100
        cv2.rectangle(parking_img, (x, 200), (x+80, 350), (200, 200, 200), 2)
    
    # Parked vehicles
    # Car 1
    cv2.rectangle(parking_img, (60, 220), (130, 280), (150, 0, 0), -1)
    cv2.circle(parking_img, (75, 280), 10, (0, 0, 0), -1)
    cv2.circle(parking_img, (115, 280), 10, (0, 0, 0), -1)
    
    # Car 2
    cv2.rectangle(parking_img, (160, 230), (230, 290), (0, 0, 150), -1)
    cv2.circle(parking_img, (175, 290), 10, (0, 0, 0), -1)
    cv2.circle(parking_img, (215, 290), 10, (0, 0, 0), -1)
    
    # SUV/Truck
    cv2.rectangle(parking_img, (360, 210), (430, 300), (100, 100, 0), -1)
    cv2.rectangle(parking_img, (370, 180), (420, 210), (120, 120, 0), -1)
    cv2.circle(parking_img, (375, 300), 12, (0, 0, 0), -1)
    cv2.circle(parking_img, (415, 300), 12, (0, 0, 0), -1)
    
    # Motorcycle
    cv2.rectangle(parking_img, (480, 240), (500, 280), (0, 100, 100), -1)
    cv2.circle(parking_img, (485, 280), 7, (0, 0, 0), -1)
    cv2.circle(parking_img, (495, 280), 7, (0, 0, 0), -1)
    
    parking_path = demo_dir / "parking_lot.jpg"
    cv2.imwrite(str(parking_path), parking_img)
    demo_images.append(parking_path)
    
    return demo_images

def benchmark_performance(detector, image_path, num_runs=5):
    """Benchmark detection performance."""
    print(f"\n⏱️  Benchmarking performance on {Path(image_path).name}...")
    
    times = []
    for i in range(num_runs):
        start_time = time.time()
        detector.process_image(image_path, save_result=False)
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"   Run {i+1}: {times[-1]:.3f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"📊 Performance Summary:")
    print(f"   Average: {avg_time:.3f}s")
    print(f"   Fastest: {min_time:.3f}s")
    print(f"   Slowest: {max_time:.3f}s")
    print(f"   FPS: {1/avg_time:.1f}")
    
    return avg_time

def test_confidence_thresholds(detector, image_path):
    """Test different confidence thresholds."""
    print(f"\n🎯 Testing confidence thresholds on {Path(image_path).name}...")
    
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = []
    
    for threshold in thresholds:
        detector.confidence_threshold = threshold
        result = detector.process_image(image_path, save_result=False)
        results.append((threshold, result['total_vehicles'], result['vehicle_counts']))
        
        print(f"   Confidence {threshold}: {result['total_vehicles']} vehicles")
        for vehicle_type, count in result['vehicle_counts'].items():
            if count > 0:
                print(f"     {vehicle_type}: {count}")
    
    return results

def demonstrate_api_usage():
    """Demonstrate programmatic API usage."""
    print(f"\n💻 Demonstrating API usage...")
    
    # Create a simple test image
    test_img = np.ones((300, 400, 3), dtype=np.uint8) * 100
    cv2.rectangle(test_img, (100, 150), (150, 200), (0, 0, 200), -1)  # Simple car shape
    cv2.circle(test_img, (110, 200), 8, (0, 0, 0), -1)
    cv2.circle(test_img, (140, 200), 8, (0, 0, 0), -1)
    
    test_path = Path("demo_images") / "api_test.jpg"
    cv2.imwrite(str(test_path), test_img)
    
    # Initialize detector
    detector = VehicleDetectionSystem(confidence_threshold=0.5)
    
    # Method 1: Direct detection
    print("🔍 Method 1: Direct detection")
    annotated_img, detection_data = detector.detect_vehicles(str(test_path))
    print(f"   Detected {detection_data['total_vehicles']} vehicles")
    
    # Method 2: Process with saving
    print("💾 Method 2: Process with automatic saving")
    result = detector.process_image(str(test_path))
    print(f"   Result saved to: {result.get('output_path', 'Not saved')}")
    
    # Method 3: Batch processing
    print("📁 Method 3: Batch processing")
    results = detector.process_batch("demo_images", output_summary=False)
    print(f"   Processed {len(results)} images")
    
    return detector

def main():
    """Main demo function."""
    print("🚗" * 20)
    print("🚗 VEHICLE DETECTION SYSTEM - COMPREHENSIVE DEMO")
    print("🚗" * 20)
    
    print("\n🎬 Starting comprehensive demonstration...")
    
    # Step 1: Create demo images
    print("\n📸 STEP 1: Creating demo images...")
    demo_images = create_demo_images()
    print(f"✅ Created {len(demo_images)} demo images")
    
    # Step 2: Initialize detection system
    print("\n🧠 STEP 2: Initializing detection system...")
    try:
        detector = VehicleDetectionSystem(confidence_threshold=0.5)
        print("✅ YOLOv8 detection system initialized successfully!")
        print(f"📦 Model: {detector.model_path}")
        print(f"🎯 Confidence threshold: {detector.confidence_threshold}")
    except Exception as e:
        print(f"❌ Failed to initialize detection system: {e}")
        return 1
    
    # Step 3: Process individual images
    print("\n🖼️  STEP 3: Processing individual images...")
    for i, image_path in enumerate(demo_images):
        print(f"\n--- Processing {image_path.name} ---")
        try:
            result = detector.process_image(str(image_path))
            print(f"✅ Success! Detected {result['total_vehicles']} vehicles")
            
            for vehicle_type, count in result['vehicle_counts'].items():
                if count > 0:
                    print(f"   {vehicle_type.title()}s: {count}")
                    
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {e}")
    
    # Step 4: Batch processing demonstration
    print("\n📁 STEP 4: Batch processing demonstration...")
    try:
        batch_results = detector.process_batch("demo_images")
        total_vehicles = sum(r['total_vehicles'] for r in batch_results)
        print(f"✅ Batch processing complete!")
        print(f"📊 Total vehicles across all images: {total_vehicles}")
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
    
    # Step 5: Confidence threshold testing
    if demo_images:
        test_confidence_thresholds(detector, str(demo_images[0]))
    
    # Step 6: Performance benchmarking
    if demo_images:
        benchmark_performance(detector, str(demo_images[0]))
    
    # Step 7: API usage demonstration
    demonstrate_api_usage()
    
    # Final summary
    print(f"\n{'='*50}")
    print("🎉 DEMO SUMMARY")
    print(f"{'='*50}")
    print(f"🎯 Total detections made: {detector.total_detections}")
    
    for vehicle_type, count in detector.detection_counts.items():
        if count > 0:
            print(f"   {vehicle_type.title()}s detected: {count}")
    
    print(f"\n📁 Output directories:")
    print(f"   🖼️  Processed images: detection_results/")
    print(f"   📸 Demo images: demo_images/")
    print(f"   📊 JSON reports: detection_results/")
    
    print(f"\n🎓 Next steps:")
    print(f"   • Run: python vehicle_detection_system.py --input your_image.jpg")
    print(f"   • Run: python test_vehicle_detection.py --download --batch")
    print(f"   • Run: python web_interface.py (for web interface)")
    
    print(f"\n✨ Demo completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())