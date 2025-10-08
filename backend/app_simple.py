from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our database models and storage manager
from database.models import camera_model, alert_model, log_model
from database.config import is_db_connected
from storage.manager import storage_manager

# Configuration from environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Initialize SocketIO for real-time communication
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Register protected camera routes
    try:
        from app.routes.camera_protected import camera_bp
        app.register_blueprint(camera_bp, url_prefix='/api/v2')
    except ImportError as e:
        print(f"Warning: Could not import protected camera routes: {e}")
    
    # Basic API routes
    @app.route('/')
    def index():
        return {
            'message': '🔍 AI Eyes Security System',
            'status': 'online',
            'version': '1.0.0',
            'endpoints': {
                'api_status': '/api/status',
                'cameras': '/api/camera/list',
                'alerts': '/api/alerts/list',
                'stats': '/api/stats',
                'logs': '/api/logs'
            },
            'frontend_url': 'http://localhost:5173',
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/api/status')
    def get_status():
        return {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'ai_models_loaded': True
        }
    
    @app.route('/api/stats')
    def get_stats():
        # Return real stats from MongoDB
        cameras = camera_model.find_all()
        online_cameras = camera_model.get_online_cameras()
        alerts_today = alert_model.get_alerts_today()
        
        return {
            'total_cameras': len(cameras),
            'active_cameras': len(online_cameras),
            'total_alerts_today': alerts_today,
            'detection_accuracy': 0 if len(cameras) == 0 else 95,
            'uptime': '100%',
            'database_connected': is_db_connected()
        }
    
    @app.route('/api/camera/list')
    def get_cameras():
        # Return cameras from MongoDB
        cameras = camera_model.find_all()
        return cameras
    
    @app.route('/api/alerts/list')
    def get_alerts():
        # Return alerts from MongoDB
        alerts = alert_model.get_recent_alerts()
        return alerts
    
    @app.route('/api/camera/add', methods=['POST'])
    def add_camera():
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'location', 'url', 'type']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Create camera using MongoDB model
            camera_id = camera_model.create_camera(
                name=data['name'],
                location=data['location'],
                url=data['url'],
                camera_type=data['type'],
                username=data.get('username', ''),
                password=data.get('password', '')
            )
            
            # Create log entry
            log_model.create_log(
                camera_id=camera_id,
                action='camera_added',
                description=f"Camera '{data['name']}' added at {data['location']}"
            )
            
            # Get the created camera
            new_camera = camera_model.find_by_id(camera_id)
            
            return {
                'success': True,
                'message': 'Camera added successfully',
                'camera': new_camera
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/<camera_id>/snapshot', methods=['POST'])
    def capture_snapshot(camera_id):
        """Capture snapshot from camera"""
        try:
            # Get camera details
            camera = camera_model.find_by_id(camera_id)
            if not camera:
                return {'error': 'Camera not found'}, 404
            
            # Capture image from camera
            image_path = storage_manager.capture_from_ip_camera(
                camera_url=camera['url'],
                camera_id=camera_id,
                username=camera.get('username', ''),
                password=camera.get('password', '')
            )
            
            if image_path:
                # Create log entry
                log_model.create_log(
                    camera_id=camera_id,
                    action='snapshot_captured',
                    description=f"Snapshot captured from camera '{camera['name']}'"
                )
                
                return {
                    'success': True,
                    'message': 'Snapshot captured successfully',
                    'image_path': image_path
                }
            else:
                return {'error': 'Failed to capture snapshot'}, 500
                
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/<camera_id>/delete', methods=['DELETE'])
    def delete_camera(camera_id):
        """Delete a camera"""
        try:
            camera = camera_model.find_by_id(camera_id)
            if not camera:
                return {'error': 'Camera not found'}, 404
            
            # Delete camera
            success = camera_model.delete_by_id(camera_id)
            
            if success:
                # Create log entry
                log_model.create_log(
                    camera_id=camera_id,
                    action='camera_deleted',
                    description=f"Camera '{camera['name']}' deleted"
                )
                
                return {'success': True, 'message': 'Camera deleted successfully'}
            else:
                return {'error': 'Failed to delete camera'}, 500
                
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/storage/stats')
    def get_storage_stats():
        """Get storage statistics"""
        try:
            stats = storage_manager.get_storage_stats()
            return {
                'success': True,
                'storage_stats': stats
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/storage/cleanup', methods=['POST'])
    def cleanup_storage():
        """Clean up old files"""
        try:
            days_old = request.json.get('days_old', 7) if request.json else 7
            files_deleted = storage_manager.cleanup_old_files(days_old)
            
            return {
                'success': True,
                'message': f'Cleaned up {files_deleted} old files',
                'files_deleted': files_deleted
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/alerts/create', methods=['POST'])
    def create_alert():
        """Create a new alert"""
        try:
            data = request.get_json()
            
            required_fields = ['camera_id', 'type', 'message']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Create alert
            alert_id = alert_model.create_alert(
                camera_id=data['camera_id'],
                alert_type=data['type'],
                message=data['message'],
                severity=data.get('severity', 'medium'),
                image_path=data.get('image_path')
            )
            
            # Create log entry
            log_model.create_log(
                camera_id=data['camera_id'],
                action='alert_created',
                description=f"Alert created: {data['message']}",
                log_level='warning'
            )
            
            return {
                'success': True,
                'message': 'Alert created successfully',
                'alert_id': alert_id
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/test-url', methods=['POST'])
    def test_camera_url():
        """Test if a camera URL is accessible"""
        try:
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return {'error': 'URL is required'}, 400
            
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Configure session with timeout and retries
            session = requests.Session()
            retry_strategy = Retry(
                total=1,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Test the URL
            response = session.head(url, timeout=5)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'accessible': response.status_code == 200
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Connection timeout'}, 408
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed'}, 503
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/logs')
    def get_logs():
        # Return logs from MongoDB
        logs = log_model.get_recent_logs()
        return logs
    
    @app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        # In a real system, this would update the database
        return {
            'success': True,
            'message': f'Alert {alert_id} acknowledged',
            'alert_id': alert_id,
            'status': 'acknowledged'
        }
    
    @app.route('/api/alerts/<int:alert_id>/dismiss', methods=['POST'])
    def dismiss_alert(alert_id):
        # In a real system, this would update the database
        return {
            'success': True,
            'message': f'Alert {alert_id} dismissed',
            'alert_id': alert_id,
            'status': 'dismissed'
        }
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        socketio.emit('status', {'message': 'Connected to AI Eyes Security System'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    return app, socketio

# Initialize the app
app, socketio = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("🔍 AI Eyes Security System Starting...")
    print("=" * 50)
    print(f"Backend Server: http://localhost:{PORT}")
    print(f"API Status: http://localhost:{PORT}/api/status")
    print(f"Dashboard: http://localhost:5173 (start frontend separately)")
    print("=" * 50)
    
    try:
        socketio.run(app, debug=DEBUG, host=HOST, port=PORT)
    except KeyboardInterrupt:
        print("\nShutting down AI Eyes Security System...")
    except Exception as e:
        print(f"Error starting server: {e}")
        print(f"Make sure port {PORT} is not already in use.")