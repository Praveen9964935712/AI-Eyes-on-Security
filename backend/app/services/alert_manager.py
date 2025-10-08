from flask_socketio import emit
from app.services.email_service import EmailAlertService
import threading
import time
from datetime import datetime

class AlertManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.email_service = EmailAlertService()
        self.active_alerts = {}
        
    def send_alert(self, alert_data):
        """Send alert through multiple channels"""
        # Add timestamp and ID
        alert_data['id'] = self._generate_alert_id()
        alert_data['timestamp'] = datetime.now().isoformat()
        
        # Store alert
        self.active_alerts[alert_data['id']] = alert_data
        
        # Send real-time notification via WebSocket
        self.socketio.emit('new_alert', alert_data)
        
        # Send email notification in background
        if alert_data.get('severity') in ['high', 'critical']:
            email_thread = threading.Thread(
                target=self.email_service.send_alert, 
                args=(alert_data,)
            )
            email_thread.daemon = True
            email_thread.start()
        
        print(f"Alert sent: {alert_data['type']} at {alert_data['location']}")
        
    def _generate_alert_id(self):
        """Generate unique alert ID"""
        return int(time.time() * 1000)  # Timestamp in milliseconds

# Global alert manager instance
alert_manager = None

def init_alert_manager(socketio):
    """Initialize global alert manager"""
    global alert_manager
    alert_manager = AlertManager(socketio)
    return alert_manager