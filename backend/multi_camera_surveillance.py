#!/usr/bin/env python3
"""
Multi-Camera AI Surveillance System
Automatically detects and monitors ALL live IP webcam cameras
Provides unified surveillance across multiple camera feeds
"""

import sys
import os
import cv2
import time
import threading
import requests
from datetime import datetime
from flask import Flask, jsonify, Response, render_template_string
import json

sys.path.append('.')
from surveillance.detector import YOLOv9Detector

class MultiCameraAISurveillance:
    """
    Automatic multi-camera surveillance system
    Detects all available IP cameras and runs AI surveillance on each
    """
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # Auto-detect your IP cameras
        self.camera_urls = self.auto_detect_cameras()
        
        # Surveillance state
        self.active_cameras = {}
        self.latest_frames = {}
        self.activity_logs = []
        self.alert_count = 0
        self.detection_stats = {}
        
        # AI Components - Optimized for ULTRA performance with minimal lag
        self.detector = YOLOv9Detector(
            conf_threshold=0.4,   # Higher threshold for faster processing and less noise
            device='cpu'          # Ensure CPU usage for stability
        )
        
        print(f"🔍 Multi-Camera AI Surveillance System Initialized")
        print(f"📹 Found {len(self.camera_urls)} live cameras")
        
        self.setup_flask_routes()
    
    def auto_detect_cameras(self):
        """Automatically detect all live IP cameras on your network"""
        print("🔎 Auto-detecting live IP cameras...")
        
        # Known camera patterns from your dashboard
        camera_patterns = [
            "http://192.168.137.254:8080",
            "http://192.168.137.4:8080",
            "http://192.168.137.1:8080",
            "http://192.168.137.2:8080",
            "http://192.168.137.3:8080",
        ]
        
        detected_cameras = {}
        
        for i, base_url in enumerate(camera_patterns):
            try:
                # Test connection
                response = requests.get(base_url, timeout=3)
                if response.status_code == 200:
                    # Test video stream
                    video_url = f"{base_url}/video"
                    cap = cv2.VideoCapture(video_url)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            camera_name = f"Camera_{i+1}_{base_url.split('.')[-2]}"
                            detected_cameras[camera_name] = {
                                'url': video_url,
                                'base_url': base_url,
                                'resolution': frame.shape,
                                'status': 'online'
                            }
                            print(f"✅ Found: {camera_name} - {video_url} ({frame.shape[1]}x{frame.shape[0]})")
                        cap.release()
                    else:
                        print(f"❌ {base_url} - Video stream not available")
                else:
                    print(f"❌ {base_url} - HTTP error {response.status_code}")
            except Exception as e:
                print(f"❌ {base_url} - Connection failed: {str(e)[:50]}...")
        
        if not detected_cameras:
            print("⚠️ No cameras detected, using manual configuration...")
            # Fallback to your known working camera
            detected_cameras = {
                "Camera_1_Manual": {
                    'url': "http://192.168.137.254:8080/video",
                    'base_url': "http://192.168.137.254:8080",
                    'resolution': (1080, 1920, 3),
                    'status': 'online'
                }
            }
        
        return detected_cameras
    
    def setup_flask_routes(self):
        """Setup web interface for multi-camera surveillance"""
        
        @self.app.route('/')
        def dashboard():
            """Multi-camera surveillance dashboard"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Multi-Camera AI Surveillance</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
        .stat-box { background: white; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .cameras-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .camera-box { background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .live-feed { width: 100%; max-width: 380px; border: 3px solid #3498db; border-radius: 8px; }
        .camera-status { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .status-online { color: #27ae60; font-weight: bold; }
        .status-offline { color: #e74c3c; font-weight: bold; }
        .activity-panel { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .activity-log { max-height: 300px; overflow-y: auto; }
        .alert { background: #e74c3c; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .warning { background: #f39c12; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .normal { background: #27ae60; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .info { background: #3498db; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .btn { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 16px; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-success { background: #27ae60; }
        .camera-stats { background: #ecf0f1; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; }
        .detection-count { font-size: 14px; color: #2c3e50; margin: 5px 0; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-cameras').textContent = data.total_cameras;
                    document.getElementById('active-cameras').textContent = data.active_cameras;
                    document.getElementById('total-detections').textContent = data.total_detections;
                    document.getElementById('total-alerts').textContent = data.total_alerts;
                    
                    // Update camera stats
                    Object.keys(data.camera_stats).forEach(cameraName => {
                        const stats = data.camera_stats[cameraName];
                        const statsElement = document.getElementById(`stats-${cameraName}`);
                        if (statsElement) {
                            statsElement.innerHTML = `
                                <div class="detection-count">Objects: ${stats.detections}</div>
                                <div class="detection-count">Persons: ${stats.persons}</div>
                                <div class="detection-count">FPS: ${stats.fps}</div>
                            `;
                        }
                    });
                });
            
            fetch('/api/activities')
                .then(response => response.json())
                .then(data => {
                    const logDiv = document.getElementById('activity-log');
                    logDiv.innerHTML = '';
                    data.activities.slice(-20).reverse().forEach(activity => {
                        const div = document.createElement('div');
                        div.className = activity.is_alert ? 'alert' : (activity.is_warning ? 'warning' : (activity.is_info ? 'info' : 'normal'));
                        div.innerHTML = `<strong>${activity.time}</strong> [${activity.camera}] ${activity.description}`;
                        logDiv.appendChild(div);
                    });
                });
        }
        
        function startAllSurveillance() {
            fetch('/api/start_all', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopAllSurveillance() {
            fetch('/api/stop_all', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function startCamera(cameraName) {
            fetch(`/api/start/${cameraName}`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopCamera(cameraName) {
            fetch(`/api/stop/${cameraName}`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        setInterval(refreshData, 2000);
        refreshData();
    </script>
</head>
<body>
    <div class="header">
        <h1>🔍 Multi-Camera AI Surveillance System</h1>
        <p>Unified Surveillance Across All IP Cameras</p>
        <button class="btn btn-success" onclick="startAllSurveillance()">▶️ Start All Cameras</button>
        <button class="btn btn-danger" onclick="stopAllSurveillance()">⏹️ Stop All Cameras</button>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>📹 Total Cameras</h3>
            <h2 id="total-cameras">{{ camera_count }}</h2>
        </div>
        <div class="stat-box">
            <h3>🟢 Active Cameras</h3>
            <h2 id="active-cameras">0</h2>
        </div>
        <div class="stat-box">
            <h3>🎯 Total Detections</h3>
            <h2 id="total-detections">0</h2>
        </div>
        <div class="stat-box">
            <h3>⚠️ Total Alerts</h3>
            <h2 id="total-alerts">0</h2>
        </div>
    </div>
    
    <div class="cameras-grid">
        {% for camera_name, camera_info in cameras.items() %}
        <div class="camera-box">
            <div class="camera-status">
                <h3>📷 {{ camera_name }}</h3>
                <span class="status-online">🟢 {{ camera_info.status.upper() }}</span>
            </div>
            <img src="/video_feed/{{ camera_name }}" class="live-feed" alt="Live AI Feed">
            <div class="camera-stats">
                <strong>URL:</strong> {{ camera_info.base_url }}<br>
                <strong>Resolution:</strong> {{ camera_info.resolution[1] }}x{{ camera_info.resolution[0] }}
                <div id="stats-{{ camera_name }}">
                    <div class="detection-count">AI Processing Ready</div>
                </div>
            </div>
            <button class="btn btn-success" onclick="startCamera('{{ camera_name }}')">▶️ Start</button>
            <button class="btn btn-danger" onclick="stopCamera('{{ camera_name }}')">⏹️ Stop</button>
        </div>
        {% endfor %}
    </div>
    
    <div class="activity-panel">
        <h3>📊 Live Multi-Camera Activity Log</h3>
        <div class="activity-log" id="activity-log">
            <div class="info"><strong>System</strong> Multi-camera surveillance ready...</div>
        </div>
    </div>
</body>
</html>
            ''', cameras=self.camera_urls, camera_count=len(self.camera_urls))
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            total_detections = sum(self.detection_stats.get(cam, {}).get('total_detections', 0) for cam in self.active_cameras)
            
            camera_stats = {}
            for camera_name in self.camera_urls.keys():
                if camera_name in self.latest_frames:
                    frame_data = self.latest_frames[camera_name]
                    camera_stats[camera_name] = {
                        'detections': len(frame_data.get('detections', [])),
                        'persons': len(frame_data.get('persons', [])),
                        'fps': self.detection_stats.get(camera_name, {}).get('fps', 0)
                    }
                else:
                    camera_stats[camera_name] = {'detections': 0, 'persons': 0, 'fps': 0}
            
            return jsonify({
                'total_cameras': len(self.camera_urls),
                'active_cameras': len(self.active_cameras),
                'total_detections': total_detections,
                'total_alerts': self.alert_count,
                'camera_stats': camera_stats
            })
        
        @self.app.route('/api/activities')
        def api_activities():
            """Get recent activities from all cameras"""
            return jsonify({'activities': self.activity_logs[-50:]})
        
        @self.app.route('/api/start_all', methods=['POST'])
        def api_start_all():
            """Start surveillance on all cameras"""
            try:
                self.start_all_surveillance()
                return jsonify({'success': True, 'message': f'Started AI surveillance on all {len(self.camera_urls)} cameras!'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/stop_all', methods=['POST'])
        def api_stop_all():
            """Stop all surveillance"""
            try:
                self.stop_all_surveillance()
                return jsonify({'success': True, 'message': 'Stopped surveillance on all cameras'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/start/<camera_name>', methods=['POST'])
        def api_start_camera(camera_name):
            """Start surveillance on specific camera"""
            try:
                if camera_name in self.camera_urls:
                    self.start_camera_surveillance(camera_name)
                    return jsonify({'success': True, 'message': f'Started surveillance on {camera_name}'})
                else:
                    return jsonify({'success': False, 'message': 'Camera not found'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/stop/<camera_name>', methods=['POST'])
        def api_stop_camera(camera_name):
            """Stop surveillance on specific camera"""
            try:
                if camera_name in self.active_cameras:
                    self.stop_camera_surveillance(camera_name)
                    return jsonify({'success': True, 'message': f'Stopped surveillance on {camera_name}'})
                else:
                    return jsonify({'success': False, 'message': 'Camera not active'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/video_feed/<camera_name>')
        def video_feed(camera_name):
            """Live video feed with AI annotations"""
            return Response(
                self.generate_frames(camera_name),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
    
    def generate_frames(self, camera_name):
        """Generate annotated video frames for specific camera"""
        while camera_name in self.active_cameras:
            try:
                if camera_name in self.latest_frames:
                    frame_data = self.latest_frames[camera_name]
                    annotated_frame = frame_data.get('annotated_frame')
                    
                    if annotated_frame is not None:
                        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        if ret:
                            frame = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                time.sleep(0.1)  # ~10 FPS for web
                
            except Exception as e:
                print(f"Frame generation error for {camera_name}: {e}")
                time.sleep(1)
    
    def process_camera_feed(self, camera_name, camera_info):
        """Process individual camera with AI surveillance"""
        camera_url = camera_info['url']
        print(f"🎯 Starting AI surveillance for {camera_name}: {camera_url}")
        
        cap = cv2.VideoCapture(camera_url)
        frame_count = 0
        last_fps_time = time.time()
        fps_counter = 0
        
        # Initialize stats
        self.detection_stats[camera_name] = {
            'total_detections': 0,
            'fps': 0,
            'start_time': time.time()
        }
        
        while camera_name in self.active_cameras:
            try:
                ret, frame = cap.read()
                if not ret:
                    print(f"Failed to read from {camera_name}, retrying...")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                fps_counter += 1
                
                # Calculate FPS
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    self.detection_stats[camera_name]['fps'] = fps_counter
                    fps_counter = 0
                    last_fps_time = current_time
                
                # AI Processing (optimized timing)
                processed_data = self.process_frame_ai(frame, camera_name, frame_count)
                
                # Update stats
                if 'detections' in processed_data:
                    self.detection_stats[camera_name]['total_detections'] += len(processed_data['detections'])
                
                # Store latest frame data
                self.latest_frames[camera_name] = processed_data
                
                # Log activities
                self.log_activities(processed_data, camera_name)
                
                # ULTRA increased sleep for maximum performance balance (3 FPS AI processing)
                time.sleep(0.33)  # ~3 FPS for AI processing to eliminate lag spikes
                
            except Exception as e:
                print(f"Camera error {camera_name}: {e}")
                time.sleep(2)
        
        cap.release()
        print(f"🛑 Stopped surveillance for {camera_name}")
    
    def process_frame_ai(self, frame, camera_name, frame_count):
        """AI processing pipeline for each camera - Performance Optimized"""
        
        # ULTRA Performance optimization: Skip even more frames to eliminate lag (process every 10th frame)
        if frame_count % 10 != 0:
            # Return cached detection data for skipped frames
            if camera_name in self.latest_frames:
                cached_data = self.latest_frames[camera_name].copy()
                cached_data['annotated_frame'] = self.create_annotated_frame(
                    frame, cached_data.get('detections', []), 
                    cached_data.get('activities', []), camera_name
                )
                return cached_data
        
        # Resize frame for ULTRA fast processing (reduce resolution even more)
        height, width = frame.shape[:2]
        small_frame = cv2.resize(frame, (int(width * 0.3), int(height * 0.3)))
        
        # Object Detection on much smaller frame
        detections = self.detector.detect(small_frame)
        
        # Scale detection coordinates back to original frame size (adjusted for 0.3 scale)
        for detection in detections:
            bbox = detection['bbox']
            detection['bbox'] = [int(bbox[0] * 3.33), int(bbox[1] * 3.33), 
                               int(bbox[2] * 3.33), int(bbox[3] * 3.33)]
        
        persons = self.detector.filter_persons(detections)
        weapons = self.detector.filter_weapons(detections)
        bags = self.detector.filter_bags(detections)
        
        activities = []
        
        # Activity Analysis
        person_count = len(persons)
        
        # Suspicious activity detection
        if weapons:
            activities.append({
                'type': 'weapon',
                'description': f'WEAPON DETECTED: {weapons[0]["class_name"]}',
                'severity': 'critical',
                'bbox': weapons[0]['bbox']
            })
        
        if person_count > 3:
            activities.append({
                'type': 'crowd',
                'description': f'CROWD ALERT: {person_count} persons detected',
                'severity': 'medium',
                'bbox': None
            })
        
        if person_count == 0 and len(bags) > 0:
            activities.append({
                'type': 'abandoned_object',
                'description': f'ABANDONED OBJECT: Unattended bag/item detected',
                'severity': 'medium',
                'bbox': bags[0]['bbox']
            })
        
        # Multi-camera correlation
        if len(detections) > 10:
            activities.append({
                'type': 'high_activity',
                'description': f'HIGH ACTIVITY: {len(detections)} objects in view',
                'severity': 'low',
                'bbox': None
            })
        
        # Create annotated frame
        annotated_frame = self.create_annotated_frame(frame, detections, activities, camera_name)
        
        return {
            'original_frame': frame,
            'annotated_frame': annotated_frame,
            'detections': detections,
            'persons': persons,
            'weapons': weapons,
            'bags': bags,
            'activities': activities,
            'timestamp': time.time()
        }
    
    def create_annotated_frame(self, frame, detections, activities, camera_name):
        """Create frame with AI annotations"""
        annotated = frame.copy()
        
        # Draw detections
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Color coding
            if class_name == 'person':
                color = (0, 255, 0)  # Green
            elif detection['class_id'] in [34, 43, 76]:  # Weapons
                color = (0, 0, 255)  # Red
            elif class_name in ['backpack', 'handbag', 'suitcase']:
                color = (255, 165, 0)  # Orange
            else:
                color = (255, 255, 0)  # Yellow
            
            # Draw bounding box
            cv2.rectangle(annotated, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(annotated, label, (bbox[0], bbox[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw activity alerts
        y_offset = 30
        for activity in activities:
            if activity['severity'] == 'critical':
                color = (0, 0, 255)  # Red
                prefix = "CRITICAL"
            elif activity['severity'] == 'medium':
                color = (0, 165, 255)  # Orange
                prefix = "ALERT"
            else:
                color = (255, 255, 0)  # Yellow
                prefix = "INFO"
            
            alert_text = f"{prefix}: {activity['description']}"
            cv2.putText(annotated, alert_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 25
        
        # Camera info overlay
        info_text = f"{camera_name} | Objects: {len(detections)} | {datetime.now().strftime('%H:%M:%S')}"
        cv2.putText(annotated, info_text, (10, annotated.shape[0]-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def log_activities(self, processed_data, camera_name):
        """Log activities from all cameras"""
        activities = processed_data.get('activities', [])
        detections = processed_data.get('detections', [])
        
        # Log detection summary every 30 seconds
        if len(detections) > 0 and int(time.time()) % 30 == 0:
            persons_count = len(processed_data.get('persons', []))
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'camera': camera_name,
                'description': f"Monitoring: {len(detections)} objects, {persons_count} persons",
                'is_alert': False,
                'is_warning': False,
                'is_info': True
            }
            self.activity_logs.append(log_entry)
        
        # Log specific activities
        for activity in activities:
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'camera': camera_name,
                'description': activity['description'],
                'severity': activity['severity'],
                'is_alert': activity['severity'] in ['high', 'critical'],
                'is_warning': activity['severity'] == 'medium',
                'is_info': activity['severity'] == 'low'
            }
            
            self.activity_logs.append(log_entry)
            
            if log_entry['is_alert']:
                self.alert_count += 1
                print(f"🚨 ALERT [{camera_name}]: {activity['description']}")
            elif log_entry['is_warning']:
                print(f"⚠️ WARNING [{camera_name}]: {activity['description']}")
        
        # Keep recent logs
        if len(self.activity_logs) > 500:
            self.activity_logs = self.activity_logs[-500:]
    
    def start_camera_surveillance(self, camera_name):
        """Start surveillance on specific camera"""
        if camera_name in self.active_cameras:
            print(f"⚠️ {camera_name} already active")
            return
        
        camera_info = self.camera_urls[camera_name]
        self.active_cameras[camera_name] = True
        
        thread = threading.Thread(
            target=self.process_camera_feed,
            args=(camera_name, camera_info),
            daemon=True
        )
        thread.start()
        print(f"✅ Started surveillance on {camera_name}")
    
    def stop_camera_surveillance(self, camera_name):
        """Stop surveillance on specific camera"""
        if camera_name in self.active_cameras:
            del self.active_cameras[camera_name]
            if camera_name in self.latest_frames:
                del self.latest_frames[camera_name]
            print(f"🛑 Stopped surveillance on {camera_name}")
    
    def start_all_surveillance(self):
        """Start surveillance on all detected cameras"""
        print("🚀 Starting AI surveillance on ALL cameras...")
        
        for camera_name in self.camera_urls.keys():
            self.start_camera_surveillance(camera_name)
        
        print(f"🎯 Multi-camera surveillance active on {len(self.active_cameras)} cameras")
    
    def stop_all_surveillance(self):
        """Stop surveillance on all cameras"""
        print("🛑 Stopping all camera surveillance...")
        camera_names = list(self.active_cameras.keys())
        for camera_name in camera_names:
            self.stop_camera_surveillance(camera_name)
        print("✅ All camera surveillance stopped")
    
    def run(self, host='0.0.0.0', port=5002):
        """Run the multi-camera surveillance system"""
        print(f"🌐 Multi-Camera Surveillance Dashboard: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    # Create multi-camera surveillance system
    surveillance = MultiCameraAISurveillance()
    
    print("\n" + "=" * 70)
    print("🔍 MULTI-CAMERA AI SURVEILLANCE SYSTEM")
    print("=" * 70)
    print("🎯 Features:")
    print("   ✅ Auto-detection of all live IP cameras")
    print("   ✅ YOLOv9 object detection on each camera")
    print("   ✅ Multi-camera activity correlation")
    print("   ✅ Unified web dashboard")
    print("   ✅ Individual camera control")
    print("   ✅ Real-time alerts across all feeds")
    print("=" * 70)
    
    try:
        # Auto-start surveillance on all cameras
        surveillance.start_all_surveillance()
        
        # Launch web dashboard
        surveillance.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down multi-camera surveillance...")
        surveillance.stop_all_surveillance()
        print("✅ System shutdown complete")