#!/usr/bin/env python3
"""
Live IP Camera Surveillance with AI
Processes your existing IP webcams for:
- Object Detection (YOLOv9) 
- Suspicious Activity Detection
- Real-time Alerts and Monitoring
"""

import sys
import os
import cv2
import numpy as np
import time
import threading
from flask import Flask, jsonify, Response, render_template_string
from datetime import datetime

# Add surveillance modules
sys.path.append('.')
from surveillance.detector import YOLOv9Detector

class LiveCameraSurveillance:
    """
    Live surveillance system for your IP cameras
    Combines object detection + activity monitoring
    """
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # Your working IP cameras
        self.camera_urls = {
            "Camera_1": "http://192.168.137.254:8080/video",
            # Add more cameras as needed
        }
        
        # Surveillance state
        self.active_cameras = {}
        self.latest_frames = {}
        self.activity_logs = []
        self.alert_count = 0
        self.detection_count = 0
        self.person_tracks = {}  # Simple person tracking
        
        # Initialize AI detector
        self.detector = YOLOv9Detector()
        
        print("🔍 Live Camera Surveillance System Initialized")
        self.setup_flask_routes()
    
    def setup_flask_routes(self):
        """Setup web interface routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main surveillance dashboard"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Live AI Surveillance</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-box { background: white; padding: 15px; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .cameras { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .camera-box { background: white; border-radius: 10px; padding: 15px; min-width: 400px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .live-feed { width: 100%; max-width: 400px; border: 3px solid #3498db; border-radius: 8px; }
        .activity-log { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-height: 400px; overflow-y: auto; }
        .alert { background: #e74c3c; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .warning { background: #f39c12; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .normal { background: #27ae60; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .btn { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 16px; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .status-online { color: #27ae60; font-weight: bold; }
        .camera-info { font-size: 12px; color: #666; margin-top: 5px; }
        .detection-info { background: #ecf0f1; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 14px; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('active-cameras').textContent = data.active_cameras;
                    document.getElementById('total-detections').textContent = data.total_detections;
                    document.getElementById('alert-count').textContent = data.alert_count;
                    document.getElementById('persons-detected').textContent = data.persons_detected;
                });
            
            fetch('/api/activities')
                .then(response => response.json())
                .then(data => {
                    const logDiv = document.getElementById('activity-log');
                    logDiv.innerHTML = '';
                    data.activities.slice(-15).reverse().forEach(activity => {
                        const div = document.createElement('div');
                        div.className = activity.is_alert ? 'alert' : (activity.is_warning ? 'warning' : 'normal');
                        div.innerHTML = `<strong>${activity.time}</strong> [${activity.camera}] ${activity.description}`;
                        logDiv.appendChild(div);
                    });
                });
        }
        
        function startSurveillance() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopSurveillance() {
            fetch('/api/stop', {method: 'POST'})
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
        <h1>🔍 Live AI Surveillance System</h1>
        <p>Real-time Object Detection + Suspicious Activity Monitoring</p>
        <button class="btn" onclick="startSurveillance()">▶️ Start Surveillance</button>
        <button class="btn btn-danger" onclick="stopSurveillance()">⏹️ Stop Surveillance</button>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>📹 Active Cameras</h3>
            <h2 id="active-cameras">0</h2>
        </div>
        <div class="stat-box">
            <h3>🎯 Total Detections</h3>
            <h2 id="total-detections">0</h2>
        </div>
        <div class="stat-box">
            <h3>⚠️ Alerts</h3>
            <h2 id="alert-count">0</h2>
        </div>
        <div class="stat-box">
            <h3>👥 Persons</h3>
            <h2 id="persons-detected">0</h2>
        </div>
    </div>
    
    <div class="cameras">
        {% for camera_name in camera_names %}
        <div class="camera-box">
            <h3>📷 {{ camera_name }}</h3>
            <img src="/video_feed/{{ camera_name }}" class="live-feed" alt="Live AI Feed">
            <p class="status-online">🟢 LIVE - AI Processing Active</p>
            <div class="camera-info">YOLOv9 Object Detection + Activity Analysis</div>
            <div class="detection-info" id="detection-{{ camera_name }}">
                Initializing AI detection...
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="activity-log">
        <h3>📊 Live Activity Log</h3>
        <div id="activity-log">
            <div class="normal"><strong>System</strong> Ready for surveillance...</div>
        </div>
    </div>
</body>
</html>
            ''', camera_names=list(self.camera_urls.keys()))
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            total_persons = 0
            for frame_data in self.latest_frames.values():
                persons = frame_data.get('persons', [])
                total_persons += len(persons)
            
            return jsonify({
                'active_cameras': len(self.active_cameras),
                'total_detections': self.detection_count,
                'alert_count': self.alert_count,
                'persons_detected': total_persons
            })
        
        @self.app.route('/api/activities')
        def api_activities():
            """Get recent activities"""
            return jsonify({'activities': self.activity_logs[-30:]})
        
        @self.app.route('/api/start', methods=['POST'])
        def api_start():
            """Start surveillance"""
            try:
                self.start_all_surveillance()
                return jsonify({'success': True, 'message': 'AI Surveillance started on all cameras!'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/stop', methods=['POST'])
        def api_stop():
            """Stop surveillance"""
            try:
                self.stop_all_surveillance()
                return jsonify({'success': True, 'message': 'Surveillance stopped'})
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
        """Generate annotated video frames"""
        while camera_name in self.active_cameras:
            try:
                if camera_name in self.latest_frames:
                    frame_data = self.latest_frames[camera_name]
                    annotated_frame = frame_data.get('annotated_frame')
                    
                    if annotated_frame is not None:
                        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if ret:
                            frame = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                time.sleep(0.1)  # ~10 FPS for web
                
            except Exception as e:
                print(f"Frame generation error for {camera_name}: {e}")
                time.sleep(1)
    
    def process_camera_feed(self, camera_name, camera_url):
        """Process camera with AI detection and activity analysis"""
        print(f"🎯 Starting AI processing for {camera_name}")
        
        cap = cv2.VideoCapture(camera_url)
        frame_count = 0
        last_person_positions = {}
        loitering_timers = {}
        
        while camera_name in self.active_cameras:
            try:
                ret, frame = cap.read()
                if not ret:
                    print(f"Failed to read from {camera_name}")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # AI Processing
                processed_data = self.process_frame_ai(frame, camera_name, frame_count, 
                                                     last_person_positions, loitering_timers)
                
                self.latest_frames[camera_name] = processed_data
                self.log_activities(processed_data, camera_name)
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Camera error {camera_name}: {e}")
                time.sleep(1)
        
        cap.release()
        print(f"🛑 Stopped {camera_name}")
    
    def process_frame_ai(self, frame, camera_name, frame_count, last_positions, loitering_timers):
        """AI processing pipeline"""
        # Object Detection
        detections = self.detector.detect(frame)
        persons = self.detector.filter_persons(detections)
        weapons = self.detector.filter_weapons(detections)
        bags = self.detector.filter_bags(detections)
        
        self.detection_count += len(detections)
        
        activities = []
        
        # Person tracking and loitering detection
        current_positions = {}
        for i, person in enumerate(persons):
            bbox = person['bbox']
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            person_id = f"person_{i}"
            current_positions[person_id] = (center_x, center_y)
            
            # Check for loitering (person staying in same area)
            if person_id in last_positions:
                prev_x, prev_y = last_positions[person_id]
                distance = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                
                if distance < 50:  # Less than 50 pixels movement
                    loitering_timers[person_id] = loitering_timers.get(person_id, 0) + 1
                    
                    # Alert after 5 seconds of loitering (150 frames at 30fps)
                    if loitering_timers[person_id] > 150:
                        activities.append({
                            'type': 'loitering',
                            'description': f'Person loitering detected - stationary for >5 seconds',
                            'bbox': bbox,
                            'severity': 'medium',
                            'person_id': person_id
                        })
                        loitering_timers[person_id] = 0  # Reset timer
                else:
                    loitering_timers[person_id] = 0  # Reset if person moved
        
        last_positions.update(current_positions)
        
        # Weapon detection
        if weapons:
            activities.append({
                'type': 'weapon',
                'description': f'WEAPON DETECTED - {weapons[0]["class_name"]} identified',
                'bbox': weapons[0]['bbox'],
                'severity': 'critical'
            })
        
        # Abandoned object detection
        if bags and len(persons) == 0:
            activities.append({
                'type': 'abandoned_object',
                'description': f'Abandoned bag/object detected with no persons nearby',
                'bbox': bags[0]['bbox'],
                'severity': 'medium'
            })
        
        # Multiple persons alert
        if len(persons) > 3:
            activities.append({
                'type': 'crowd',
                'description': f'Crowd detected - {len(persons)} persons in view',
                'bbox': None,
                'severity': 'low'
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
            
            # Colors based on object type
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
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
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
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
        
        # Add info overlay
        info_text = f"{camera_name} | Objects: {len(detections)} | " + datetime.now().strftime("%H:%M:%S")
        cv2.putText(annotated, info_text, (10, annotated.shape[0]-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def log_activities(self, processed_data, camera_name):
        """Log activities and alerts"""
        activities = processed_data.get('activities', [])
        detections = processed_data.get('detections', [])
        
        # Log detections summary every 10 seconds
        if len(detections) > 0 and int(time.time()) % 10 == 0:
            persons_count = len(processed_data.get('persons', []))
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'camera': camera_name,
                'description': f"Monitoring: {len(detections)} objects detected, {persons_count} persons",
                'is_alert': False,
                'is_warning': False
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
                'is_warning': activity['severity'] == 'medium'
            }
            
            self.activity_logs.append(log_entry)
            
            if log_entry['is_alert']:
                self.alert_count += 1
                print(f"🚨 ALERT [{camera_name}]: {activity['description']}")
            elif log_entry['is_warning']:
                print(f"⚠️ WARNING [{camera_name}]: {activity['description']}")
        
        # Keep only recent logs
        if len(self.activity_logs) > 200:
            self.activity_logs = self.activity_logs[-200:]
    
    def start_all_surveillance(self):
        """Start surveillance on all cameras"""
        print("🚀 Starting Live AI Surveillance...")
        
        for camera_name, camera_url in self.camera_urls.items():
            try:
                cap = cv2.VideoCapture(camera_url)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✅ {camera_name} - Connected and processing")
                        
                        self.active_cameras[camera_name] = True
                        thread = threading.Thread(
                            target=self.process_camera_feed,
                            args=(camera_name, camera_url),
                            daemon=True
                        )
                        thread.start()
                    else:
                        print(f"❌ {camera_name} - Cannot read frames")
                else:
                    print(f"❌ {camera_name} - Cannot connect to {camera_url}")
                cap.release()
            except Exception as e:
                print(f"❌ {camera_name} - Error: {e}")
        
        if self.active_cameras:
            print(f"🎯 AI Surveillance active on {len(self.active_cameras)} camera(s)")
        else:
            print("❌ No cameras available")
    
    def stop_all_surveillance(self):
        """Stop all surveillance"""
        print("🛑 Stopping surveillance...")
        self.active_cameras.clear()
        self.latest_frames.clear()
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the surveillance system"""
        print(f"🌐 Web interface starting at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    surveillance = LiveCameraSurveillance()
    
    print("🔍 Live AI Surveillance System Ready!")
    print("📱 Features:")
    print("   ✅ YOLOv9 Object Detection")
    print("   ✅ Person Tracking & Loitering Detection") 
    print("   ✅ Weapon Detection Alerts")
    print("   ✅ Abandoned Object Detection")
    print("   ✅ Real-time Activity Monitoring")
    print("   ✅ Live Web Interface")
    print()
    
    try:
        surveillance.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        surveillance.stop_all_surveillance()