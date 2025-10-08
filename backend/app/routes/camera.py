from flask import Blueprint, jsonify, request, Response
import cv2
import json

# Create camera service instance with error handling
try:
    from app.services.camera_service import CameraService
    camera_service = CameraService()
except ImportError:
    print("Warning: CameraService not available")
    camera_service = None

camera_bp = Blueprint('camera', __name__)

@camera_bp.route('/list', methods=['GET'])
def get_cameras():
    """Get list of all cameras"""
    cameras = [
        {
            'id': 1,
            'name': 'Farm Gate A',
            'location': 'Main Entrance',
            'status': 'online',
            'url': 'http://192.168.1.100:8080/video',
            'type': 'farm'
        },
        {
            'id': 2,
            'name': 'Bank Main Hall',
            'location': 'Customer Area', 
            'status': 'online',
            'url': 'http://192.168.1.101:8080/video',
            'type': 'bank'
        },
        {
            'id': 3,
            'name': 'Farm Perimeter',
            'location': 'North Side',
            'status': 'online',
            'url': 'http://192.168.1.102:8080/video',
            'type': 'farm'
        },
        {
            'id': 4,
            'name': 'Bank ATM Area',
            'location': 'ATM Zone',
            'status': 'online',
            'url': 'http://192.168.1.103:8080/video',
            'type': 'bank'
        },
        {
            'id': 5,
            'name': 'Farm Storage',
            'location': 'Equipment Barn',
            'status': 'offline',
            'url': 'http://192.168.1.104:8080/video',
            'type': 'farm'
        },
        {
            'id': 6,
            'name': 'Bank Vault Area',
            'location': 'Restricted Zone',
            'status': 'online',
            'url': 'http://192.168.1.105:8080/video',
            'type': 'bank'
        }
    ]
    return jsonify(cameras)

@camera_bp.route('/stream/<int:camera_id>')
def video_stream(camera_id):
    """Stream video from specific camera"""
    def generate():
        # This would connect to actual camera stream
        # For now, we'll simulate with placeholder
        while True:
            # Get frame from camera service
            frame = camera_service.get_frame(camera_id)
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/<int:camera_id>/snapshot', methods=['POST'])
def take_snapshot(camera_id):
    """Take a snapshot from specific camera"""
    success = camera_service.take_snapshot(camera_id)
    if success:
        return jsonify({'message': 'Snapshot saved successfully', 'camera_id': camera_id})
    else:
        return jsonify({'error': 'Failed to take snapshot'}), 500

@camera_bp.route('/<int:camera_id>/record', methods=['POST'])
def toggle_recording(camera_id):
    """Start/stop recording for specific camera"""
    action = request.json.get('action', 'start')
    success = camera_service.toggle_recording(camera_id, action == 'start')
    
    if success:
        return jsonify({
            'message': f'Recording {"started" if action == "start" else "stopped"}',
            'camera_id': camera_id,
            'recording': action == 'start'
        })
    else:
        return jsonify({'error': 'Failed to toggle recording'}), 500

@camera_bp.route('/add', methods=['POST'])
def add_camera():
    """Add new camera to the system"""
    data = request.get_json()
    required_fields = ['name', 'location', 'url', 'type']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Here you would add camera to database
    new_camera = {
        'id': 7,  # This would be auto-generated
        'name': data['name'],
        'location': data['location'],
        'url': data['url'],
        'type': data['type'],
        'status': 'online'
    }
    
    return jsonify({'message': 'Camera added successfully', 'camera': new_camera})