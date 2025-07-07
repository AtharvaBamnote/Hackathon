#!/usr/bin/env python3
"""
Vehicle Detection System
========================

A comprehensive computer vision system for detecting, classifying, and counting 
vehicles in traffic images using YOLOv8.

Features:
- Detect cars, trucks, motorcycles, and other vehicles
- Display bounding boxes with confidence scores
- Count vehicles by category
- Save annotated results
- Support for both images and video processing

Author: AI Assistant
Date: 2025
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import json
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

try:
    from ultralytics import YOLO
except ImportError:
    print("Installing ultralytics...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
    from ultralytics import YOLO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VehicleDetectionSystem:
    """
    A comprehensive vehicle detection system using YOLOv8.
    """
    
    # Vehicle class mapping for COCO dataset
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle', 
        5: 'bus',
        7: 'truck'
    }
    
    # Colors for different vehicle types (BGR format for OpenCV)
    CLASS_COLORS = {
        'car': (0, 255, 0),      # Green
        'motorcycle': (255, 0, 0),  # Blue  
        'bus': (0, 165, 255),    # Orange
        'truck': (0, 0, 255)     # Red
    }
    
    def __init__(self, model_path: str = 'yolov8n.pt', confidence_threshold: float = 0.5):
        """
        Initialize the vehicle detection system.
        
        Args:
            model_path: Path to YOLOv8 model weights
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.model = None
        self.results_dir = Path("detection_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.total_detections = 0
        self.detection_counts = {vehicle: 0 for vehicle in self.VEHICLE_CLASSES.values()}
        
        self._load_model()
    
    def _load_model(self):
        """Load the YOLOv8 model."""
        try:
            logger.info(f"Loading YOLOv8 model: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def detect_vehicles(self, image_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Detect vehicles in an image.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Tuple of (annotated_image, detection_results)
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Run inference
        results = self.model(image, conf=self.confidence_threshold)
        
        # Process detections
        detection_data = self._process_detections(image, results[0])
        
        # Draw annotations
        annotated_image = self._draw_annotations(image.copy(), detection_data['detections'])
        
        return annotated_image, detection_data
    
    def _process_detections(self, image: np.ndarray, result) -> Dict[str, Any]:
        """
        Process detection results and extract vehicle information.
        
        Args:
            image: Input image
            result: YOLO detection result
            
        Returns:
            Dictionary containing detection information
        """
        detections = []
        vehicle_counts = {vehicle: 0 for vehicle in self.VEHICLE_CLASSES.values()}
        
        if result.boxes is not None:
            for box in result.boxes:
                # Get detection data
                class_id = int(box.cls.cpu().numpy())
                confidence = float(box.conf.cpu().numpy())
                bbox = box.xyxy.cpu().numpy()[0]  # [x1, y1, x2, y2]
                
                # Check if it's a vehicle class
                if class_id in self.VEHICLE_CLASSES:
                    vehicle_type = self.VEHICLE_CLASSES[class_id]
                    
                    # Store detection
                    detection = {
                        'vehicle_type': vehicle_type,
                        'confidence': confidence,
                        'bbox': bbox.tolist(),
                        'class_id': class_id
                    }
                    detections.append(detection)
                    
                    # Update counts
                    vehicle_counts[vehicle_type] += 1
                    self.detection_counts[vehicle_type] += 1
        
        total_vehicles = sum(vehicle_counts.values())
        self.total_detections += total_vehicles
        
        return {
            'detections': detections,
            'vehicle_counts': vehicle_counts,
            'total_vehicles': total_vehicles,
            'image_shape': image.shape
        }
    
    def _draw_annotations(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the image.
        
        Args:
            image: Input image
            detections: List of detection dictionaries
            
        Returns:
            Annotated image
        """
        for detection in detections:
            bbox = detection['bbox']
            vehicle_type = detection['vehicle_type']
            confidence = detection['confidence']
            
            # Extract coordinates
            x1, y1, x2, y2 = map(int, bbox)
            
            # Get color for vehicle type
            color = self.CLASS_COLORS.get(vehicle_type, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label = f"{vehicle_type}: {confidence:.2f}"
            
            # Calculate label size and position
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Draw label background
            cv2.rectangle(
                image, 
                (x1, y1 - label_height - baseline - 5),
                (x1 + label_width, y1),
                color, -1
            )
            
            # Draw label text
            cv2.putText(
                image, label, (x1, y1 - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        return image
    
    def add_summary_text(self, image: np.ndarray, vehicle_counts: Dict[str, int]) -> np.ndarray:
        """
        Add summary text with vehicle counts to the image.
        
        Args:
            image: Input image
            vehicle_counts: Dictionary of vehicle counts
            
        Returns:
            Image with summary text
        """
        height, width = image.shape[:2]
        
        # Prepare summary text
        summary_lines = ["Vehicle Detection Summary:"]
        total = sum(vehicle_counts.values())
        summary_lines.append(f"Total Vehicles: {total}")
        
        for vehicle_type, count in vehicle_counts.items():
            if count > 0:
                summary_lines.append(f"{vehicle_type.title()}s: {count}")
        
        # Add background for text
        text_height = 30 * len(summary_lines)
        cv2.rectangle(image, (10, 10), (350, text_height + 20), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (350, text_height + 20), (255, 255, 255), 2)
        
        # Add text
        for i, line in enumerate(summary_lines):
            y_pos = 35 + (i * 25)
            cv2.putText(
                image, line, (20, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
        
        return image
    
    def process_image(self, image_path: str, save_result: bool = True) -> Dict[str, Any]:
        """
        Complete pipeline to process a single image.
        
        Args:
            image_path: Path to input image
            save_result: Whether to save the annotated result
            
        Returns:
            Detection results dictionary
        """
        logger.info(f"Processing image: {image_path}")
        
        try:
            # Detect vehicles
            annotated_image, detection_data = self.detect_vehicles(image_path)
            
            # Add summary text
            final_image = self.add_summary_text(annotated_image, detection_data['vehicle_counts'])
            
            # Save result if requested
            if save_result:
                input_path = Path(image_path)
                output_path = self.results_dir / f"detected_{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(str(output_path), final_image)
                logger.info(f"Result saved: {output_path}")
                detection_data['output_path'] = str(output_path)
            
            # Log results
            logger.info(f"Detection complete: {detection_data['total_vehicles']} vehicles found")
            for vehicle_type, count in detection_data['vehicle_counts'].items():
                if count > 0:
                    logger.info(f"  {vehicle_type.title()}s: {count}")
            
            return detection_data
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            raise
    
    def process_batch(self, image_directory: str, output_summary: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple images in a directory.
        
        Args:
            image_directory: Directory containing images
            output_summary: Whether to save a summary report
            
        Returns:
            List of detection results for each image
        """
        image_dir = Path(image_directory)
        if not image_dir.exists():
            raise ValueError(f"Directory not found: {image_directory}")
        
        # Find image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_files = [f for f in image_dir.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        if not image_files:
            logger.warning(f"No image files found in {image_directory}")
            return []
        
        logger.info(f"Processing {len(image_files)} images...")
        
        results = []
        for image_file in image_files:
            try:
                result = self.process_image(str(image_file))
                result['input_file'] = str(image_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {e}")
        
        # Generate summary report
        if output_summary and results:
            self._generate_summary_report(results)
        
        return results
    
    def _generate_summary_report(self, results: List[Dict[str, Any]]):
        """Generate a summary report of batch processing results."""
        report_path = self.results_dir / f"detection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Calculate statistics
        total_images = len(results)
        total_vehicles = sum(r['total_vehicles'] for r in results)
        
        # Vehicle type statistics
        vehicle_stats = {vehicle: 0 for vehicle in self.VEHICLE_CLASSES.values()}
        for result in results:
            for vehicle_type, count in result['vehicle_counts'].items():
                vehicle_stats[vehicle_type] += count
        
        # Create summary
        summary = {
            'processing_date': datetime.now().isoformat(),
            'total_images_processed': total_images,
            'total_vehicles_detected': total_vehicles,
            'average_vehicles_per_image': total_vehicles / total_images if total_images > 0 else 0,
            'vehicle_type_statistics': vehicle_stats,
            'detailed_results': results
        }
        
        # Save summary
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary report saved: {report_path}")
        
        # Print summary to console
        print("\n" + "="*50)
        print("VEHICLE DETECTION SUMMARY")
        print("="*50)
        print(f"Images processed: {total_images}")
        print(f"Total vehicles detected: {total_vehicles}")
        print(f"Average vehicles per image: {total_vehicles/total_images:.1f}")
        print("\nVehicle type breakdown:")
        for vehicle_type, count in vehicle_stats.items():
            if count > 0:
                percentage = (count / total_vehicles) * 100 if total_vehicles > 0 else 0
                print(f"  {vehicle_type.title()}s: {count} ({percentage:.1f}%)")
        print("="*50)
    
    def process_video(self, video_path: str, output_path: str = None, skip_frames: int = 1):
        """
        Process video file for vehicle detection.
        
        Args:
            video_path: Path to input video
            output_path: Path for output video (optional)
            skip_frames: Process every nth frame for speed
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Processing video: {video_path}")
        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        # Set up output video writer if path provided
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every nth frame
                if frame_count % skip_frames == 0:
                    # Run detection on frame
                    results = self.model(frame, conf=self.confidence_threshold)
                    detection_data = self._process_detections(frame, results[0])
                    
                    # Annotate frame
                    annotated_frame = self._draw_annotations(frame.copy(), detection_data['detections'])
                    annotated_frame = self.add_summary_text(annotated_frame, detection_data['vehicle_counts'])
                    
                    # Write frame to output video
                    if out:
                        out.write(annotated_frame)
                    
                    # Display progress
                    if frame_count % (fps * 5) == 0:  # Every 5 seconds
                        progress = (frame_count / total_frames) * 100
                        logger.info(f"Progress: {progress:.1f}%")
                
                frame_count += 1
                
        finally:
            cap.release()
            if out:
                out.release()
            
        logger.info(f"Video processing complete. Processed {frame_count} frames.")


def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(description="Vehicle Detection System")
    parser.add_argument("--input", "-i", required=True, help="Input image/video/directory path")
    parser.add_argument("--output", "-o", help="Output path (optional)")
    parser.add_argument("--confidence", "-c", type=float, default=0.5, 
                       help="Confidence threshold (default: 0.5)")
    parser.add_argument("--model", "-m", default="yolov8n.pt", 
                       help="YOLOv8 model path (default: yolov8n.pt)")
    parser.add_argument("--batch", "-b", action="store_true", 
                       help="Process directory of images")
    parser.add_argument("--video", "-v", action="store_true", 
                       help="Process video file")
    
    args = parser.parse_args()
    
    # Initialize detection system
    detector = VehicleDetectionSystem(
        model_path=args.model,
        confidence_threshold=args.confidence
    )
    
    try:
        if args.video:
            # Process video
            output_path = args.output or f"detected_{Path(args.input).stem}.mp4"
            detector.process_video(args.input, output_path)
            
        elif args.batch:
            # Process batch of images
            detector.process_batch(args.input)
            
        else:
            # Process single image
            detector.process_image(args.input)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())