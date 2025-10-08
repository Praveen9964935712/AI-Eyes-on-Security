from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.settings import *

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Initialize SocketIO for real-time communication
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Import and register routes
    try:
        from app.routes.api import api_bp
        from app.routes.camera import camera_bp
        from app.routes.alerts import alerts_bp
        
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(camera_bp, url_prefix='/api/camera')
        app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    except ImportError as e:
        print(f"Warning: Could not import routes: {e}")
        # Register basic routes directly
        @app.route('/api/status')
        def status():
            return {'status': 'online', 'message': 'AI Eyes Security System is running'}
    
    return app, socketio

# Initialize the app
app, socketio = create_app()

if __name__ == '__main__':
    print("Starting AI Eyes Security System...")
    print("Dashboard will be available at: http://localhost:5000")
    print("API endpoints: http://localhost:5000/api/")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)