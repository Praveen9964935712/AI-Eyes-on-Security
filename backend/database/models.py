"""
Database Models for AI Eyes Security System
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from database.config import get_database, is_db_connected, CAMERAS_COLLECTION, ALERTS_COLLECTION, LOGS_COLLECTION

class BaseModel:
    """Base model with common database operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._fallback_storage = []  # Fallback for when MongoDB is not available
    
    @property
    def collection(self):
        """Get collection from database or use fallback"""
        db = get_database()
        if db is not None:
            return db[self.collection_name]
        return None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all documents"""
        if self.collection is not None:
            try:
                documents = list(self.collection.find())
                # Convert ObjectId to string for JSON serialization
                for doc in documents:
                    if '_id' in doc:
                        doc['id'] = str(doc['_id'])
                        del doc['_id']
                return documents
            except Exception as e:
                print(f"Database error in find_all: {e}")
        
        # Fallback to in-memory storage
        return self._fallback_storage.copy()
    
    def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        if self.collection is not None:
            try:
                if isinstance(doc_id, str) and len(doc_id) == 24:
                    # MongoDB ObjectId
                    doc = self.collection.find_one({"_id": ObjectId(doc_id)})
                else:
                    # Regular ID
                    doc = self.collection.find_one({"id": int(doc_id) if doc_id.isdigit() else doc_id})
                
                if doc:
                    doc['id'] = str(doc['_id']) if '_id' in doc else doc.get('id')
                    if '_id' in doc:
                        del doc['_id']
                    return doc
            except Exception as e:
                print(f"Database error in find_by_id: {e}")
        
        # Fallback to in-memory storage
        for item in self._fallback_storage:
            if str(item.get('id')) == str(doc_id):
                return item
        return None
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a document and return ID"""
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        
        if self.collection is not None:
            try:
                result = self.collection.insert_one(document)
                return str(result.inserted_id)
            except Exception as e:
                print(f"Database error in insert_one: {e}")
        
        # Fallback to in-memory storage
        if 'id' not in document:
            document['id'] = len(self._fallback_storage) + 1
        self._fallback_storage.append(document)
        return str(document['id'])
    
    def update_by_id(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        update_data['updated_at'] = datetime.utcnow()
        
        if self.collection is not None:
            try:
                if isinstance(doc_id, str) and len(doc_id) == 24:
                    result = self.collection.update_one(
                        {"_id": ObjectId(doc_id)}, 
                        {"$set": update_data}
                    )
                else:
                    result = self.collection.update_one(
                        {"id": int(doc_id) if doc_id.isdigit() else doc_id}, 
                        {"$set": update_data}
                    )
                return result.modified_count > 0
            except Exception as e:
                print(f"Database error in update_by_id: {e}")
        
        # Fallback to in-memory storage
        for i, item in enumerate(self._fallback_storage):
            if str(item.get('id')) == str(doc_id):
                self._fallback_storage[i].update(update_data)
                return True
        return False
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID"""
        if self.collection is not None:
            try:
                if isinstance(doc_id, str) and len(doc_id) == 24:
                    result = self.collection.delete_one({"_id": ObjectId(doc_id)})
                else:
                    result = self.collection.delete_one({"id": int(doc_id) if doc_id.isdigit() else doc_id})
                return result.deleted_count > 0
            except Exception as e:
                print(f"Database error in delete_by_id: {e}")
        
        # Fallback to in-memory storage
        for i, item in enumerate(self._fallback_storage):
            if str(item.get('id')) == str(doc_id):
                del self._fallback_storage[i]
                return True
        return False

class CameraModel(BaseModel):
    """Camera model for managing IP cameras and webcams"""
    
    def __init__(self):
        super().__init__(CAMERAS_COLLECTION)
    
    def create_camera(self, name: str, location: str, url: str, camera_type: str, 
                     username: str = "", password: str = "") -> str:
        """Create a new camera"""
        camera_data = {
            'name': name,
            'location': location,
            'url': url,
            'type': camera_type,
            'username': username,
            'password': password,
            'status': 'online',
            'last_seen': datetime.utcnow(),
            'recording': False,
            'motion_detection': True,
            'ai_detection': True
        }
        
        # Generate ID for fallback storage
        if not is_db_connected():
            camera_data['id'] = len(self._fallback_storage) + 1
        
        return self.insert_one(camera_data)
    
    def get_online_cameras(self) -> List[Dict[str, Any]]:
        """Get all online cameras"""
        if self.collection is not None:
            try:
                cameras = list(self.collection.find({"status": "online"}))
                for camera in cameras:
                    if '_id' in camera:
                        camera['id'] = str(camera['_id'])
                        del camera['_id']
                return cameras
            except Exception as e:
                print(f"Database error in get_online_cameras: {e}")
        
        # Fallback
        return [cam for cam in self._fallback_storage if cam.get('status') == 'online']
    
    def update_camera_status(self, camera_id: str, status: str) -> bool:
        """Update camera status"""
        return self.update_by_id(camera_id, {
            'status': status,
            'last_seen': datetime.utcnow()
        })

class AlertModel(BaseModel):
    """Alert model for security events"""
    
    def __init__(self):
        super().__init__(ALERTS_COLLECTION)
    
    def create_alert(self, camera_id: str, alert_type: str, message: str, 
                    severity: str = "medium", image_path: Optional[str] = None) -> str:
        """Create a new alert"""
        alert_data = {
            'camera_id': camera_id,
            'type': alert_type,
            'message': message,
            'severity': severity,  # low, medium, high, critical
            'image_path': image_path,
            'timestamp': datetime.utcnow(),
            'resolved': False,
            'acknowledged': False
        }
        
        if not is_db_connected():
            alert_data['id'] = len(self._fallback_storage) + 1
        
        return self.insert_one(alert_data)
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        if self.collection is not None:
            try:
                alerts = list(self.collection.find().sort("timestamp", -1).limit(limit))
                for alert in alerts:
                    if '_id' in alert:
                        alert['id'] = str(alert['_id'])
                        del alert['_id']
                return alerts
            except Exception as e:
                print(f"Database error in get_recent_alerts: {e}")
        
        # Fallback
        sorted_alerts = sorted(self._fallback_storage, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        return sorted_alerts[:limit]
    
    def get_alerts_today(self) -> int:
        """Get count of alerts today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.collection is not None:
            try:
                return self.collection.count_documents({"timestamp": {"$gte": today_start}})
            except Exception as e:
                print(f"Database error in get_alerts_today: {e}")
        
        # Fallback
        return len([a for a in self._fallback_storage if a.get('timestamp', datetime.min) >= today_start])

class LogModel(BaseModel):
    """Log model for system events"""
    
    def __init__(self):
        super().__init__(LOGS_COLLECTION)
    
    def create_log(self, camera_id: str, action: str, description: str, log_level: str = "info") -> str:
        """Create a new log entry"""
        log_data = {
            'camera_id': camera_id,
            'action': action,
            'description': description,
            'level': log_level,  # debug, info, warning, error, critical
            'timestamp': datetime.utcnow(),
            'user_agent': 'AI Eyes System'
        }
        
        if not is_db_connected():
            log_data['id'] = len(self._fallback_storage) + 1
        
        return self.insert_one(log_data)
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        if self.collection is not None:
            try:
                logs = list(self.collection.find().sort("timestamp", -1).limit(limit))
                for log in logs:
                    if '_id' in log:
                        log['id'] = str(log['_id'])
                        del log['_id']
                return logs
            except Exception as e:
                print(f"Database error in get_recent_logs: {e}")
        
        # Fallback
        sorted_logs = sorted(self._fallback_storage, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        return sorted_logs[:limit]

# Global model instances
camera_model = CameraModel()
alert_model = AlertModel()
log_model = LogModel()