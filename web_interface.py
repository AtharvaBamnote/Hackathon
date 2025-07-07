#!/usr/bin/env python3
"""
Web Interface for Vehicle Detection System
==========================================

A Flask-based web interface that allows users to upload images
and view vehicle detection results through a browser.

Features:
- Image upload via web form
- Real-time processing and results display
- Download processed images
- View detection statistics

Usage:
    python web_interface.py
    
Then open http://localhost:5000 in your browser
"""

import os
import json
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

try:
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
except ImportError:
    print("Installing Flask...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask"])
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

import cv2
import numpy as np
from PIL import Image
from vehicle_detection_system import VehicleDetectionSystem

app = Flask(__name__)
app.secret_key = 'vehicle_detection_secret_key_2025'

# Configuration
UPLOAD_FOLDER = 'web_uploads'
RESULTS_FOLDER = 'web_results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(RESULTS_FOLDER).mkdir(exist_ok=True)

# Initialize detection system
detector = None

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_detector():
    """Initialize the vehicle detection system."""
    global detector
    if detector is None:
        try:
            detector = VehicleDetectionSystem(confidence_threshold=0.5)
            return True
        except Exception as e:
            print(f"Error initializing detector: {e}")
            return False
    return True

def encode_image_to_base64(image_path):
    """Convert image to base64 for web display."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    if not init_detector():
        flash('Error: Could not initialize detection system', 'error')
        return redirect(url_for('index'))
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    confidence = float(request.form.get('confidence', 0.5))
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Update detector confidence
            detector.confidence_threshold = confidence
            
            # Process image
            annotated_image, detection_data = detector.detect_vehicles(filepath)
            final_image = detector.add_summary_text(annotated_image, detection_data['vehicle_counts'])
            
            # Save result
            result_filename = f"result_{filename}"
            result_path = os.path.join(RESULTS_FOLDER, result_filename)
            cv2.imwrite(result_path, final_image)
            
            # Prepare data for display
            result_data = {
                'original_filename': file.filename,
                'processed_filename': result_filename,
                'detection_data': detection_data,
                'confidence_threshold': confidence,
                'processing_time': datetime.now().isoformat()
            }
            
            # Encode images for display
            original_b64 = encode_image_to_base64(filepath)
            result_b64 = encode_image_to_base64(result_path)
            
            result_data['original_image_b64'] = original_b64
            result_data['result_image_b64'] = result_b64
            
            return render_template('results.html', **result_data)
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload an image file.', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed image."""
    try:
        return send_file(
            os.path.join(RESULTS_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/detect', methods=['POST'])
def api_detect():
    """API endpoint for programmatic access."""
    if not init_detector():
        return jsonify({'error': 'Could not initialize detection system'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    confidence = float(request.form.get('confidence', 0.5))
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        temp_filename = f"temp_{timestamp}_{file.filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        
        # Update detector confidence
        detector.confidence_threshold = confidence
        
        # Process image
        _, detection_data = detector.detect_vehicles(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'total_vehicles': detection_data['total_vehicles'],
            'vehicle_counts': detection_data['vehicle_counts'],
            'detections': detection_data['detections'],
            'confidence_threshold': confidence
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Create index.html
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Detection System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .upload-area {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background-color: #f8f9fa;
            margin: 2rem 0;
        }
        .feature-icon {
            font-size: 3rem;
            color: #007bff;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <h1 class="text-center mb-4">🚗 Vehicle Detection System</h1>
                <p class="text-center text-muted mb-4">
                    Upload an image to automatically detect and count vehicles using AI
                </p>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <div class="upload-area">
                    <form method="post" action="/upload" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="file" class="form-label">
                                <div class="feature-icon">📸</div>
                                <h5>Select Image File</h5>
                            </label>
                            <input type="file" class="form-control" id="file" name="file" 
                                   accept=".jpg,.jpeg,.png,.bmp,.tiff" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="confidence" class="form-label">Confidence Threshold</label>
                            <input type="range" class="form-range" id="confidence" name="confidence" 
                                   min="0.1" max="0.9" step="0.1" value="0.5">
                            <div class="d-flex justify-content-between">
                                <small>0.1 (More detections)</small>
                                <small id="confidence-value">0.5</small>
                                <small>0.9 (Fewer, higher confidence)</small>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-lg">
                            🔍 Detect Vehicles
                        </button>
                    </form>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-3 text-center">
                        <div class="feature-icon">🚗</div>
                        <h6>Cars</h6>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="feature-icon">🏍️</div>
                        <h6>Motorcycles</h6>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="feature-icon">🚛</div>
                        <h6>Trucks</h6>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="feature-icon">🚌</div>
                        <h6>Buses</h6>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const confidenceSlider = document.getElementById('confidence');
        const confidenceValue = document.getElementById('confidence-value');
        
        confidenceSlider.addEventListener('input', function() {
            confidenceValue.textContent = this.value;
        });
    </script>
</body>
</html>'''
    
    # Create results.html
    results_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detection Results - Vehicle Detection System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .result-image {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .stats-card {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .vehicle-stat {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 0.75rem;
            margin: 0.5rem 0;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-10 mx-auto">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1>🎯 Detection Results</h1>
                    <a href="/" class="btn btn-outline-primary">Upload Another Image</a>
                </div>
                
                <div class="row">
                    <div class="col-md-8">
                        <h3>Processed Image</h3>
                        <img src="data:image/jpeg;base64,{{ result_image_b64 }}" 
                             class="result-image" alt="Detection Results">
                        
                        <div class="mt-3">
                            <a href="/download/{{ processed_filename }}" class="btn btn-success">
                                💾 Download Result
                            </a>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="stats-card">
                            <h4>📊 Detection Summary</h4>
                            <div class="text-center">
                                <h2>{{ detection_data.total_vehicles }}</h2>
                                <p>Total Vehicles Detected</p>
                            </div>
                            
                            {% for vehicle_type, count in detection_data.vehicle_counts.items() %}
                                {% if count > 0 %}
                                <div class="vehicle-stat">
                                    <div class="d-flex justify-content-between">
                                        <span>{{ vehicle_type.title() }}s:</span>
                                        <strong>{{ count }}</strong>
                                    </div>
                                </div>
                                {% endif %}
                            {% endfor %}
                            
                            <hr style="border-color: rgba(255,255,255,0.3);">
                            <small>
                                <strong>Confidence Threshold:</strong> {{ confidence_threshold }}<br>
                                <strong>Processing Time:</strong> {{ processing_time[:19] }}
                            </small>
                        </div>
                        
                        <h5>Original Image</h5>
                        <img src="data:image/jpeg;base64,{{ original_image_b64 }}" 
                             class="result-image" style="max-height: 200px;" alt="Original Image">
                    </div>
                </div>
                
                {% if detection_data.detections %}
                <div class="mt-4">
                    <h4>🔍 Detection Details</h4>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Vehicle Type</th>
                                    <th>Confidence</th>
                                    <th>Bounding Box</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for detection in detection_data.detections %}
                                <tr>
                                    <td>
                                        <span class="badge bg-primary">{{ detection.vehicle_type.title() }}</span>
                                    </td>
                                    <td>{{ "%.2f"|format(detection.confidence) }}</td>
                                    <td>
                                        <small>
                                            ({{ "%.0f"|format(detection.bbox[0]) }}, {{ "%.0f"|format(detection.bbox[1]) }}) 
                                            to 
                                            ({{ "%.0f"|format(detection.bbox[2]) }}, {{ "%.0f"|format(detection.bbox[3]) }})
                                        </small>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Write templates to files
    with open(templates_dir / 'index.html', 'w') as f:
        f.write(index_html)
    
    with open(templates_dir / 'results.html', 'w') as f:
        f.write(results_html)

if __name__ == '__main__':
    print("🚗 Starting Vehicle Detection Web Interface...")
    
    # Create templates
    create_templates()
    print("✅ Templates created")
    
    # Initialize detector
    if init_detector():
        print("✅ Detection system initialized")
    else:
        print("❌ Warning: Detection system failed to initialize")
    
    print("\n🌐 Web interface starting...")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("📤 Upload an image to test vehicle detection")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)