"""
Database Models for AI Eyes Security System
MongoDB-only storage (no JSON fallback)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from database.config import get_database, is_db_connected, CAMERAS_COLLECTION, ALERTS_COLLECTION, LOGS_COLLECTION

class BaseModel:
    """Base model with MongoDB-only operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    @property
    def collection(self):
        """Get collection from database"""
        db = get_database()
        if db is not None:
            return db[self.collection_name]
        return None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all documents"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return []
            
        try:
            documents = list(self.collection.find())
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['id'] = str(doc['_id'])
                    del doc['_id']
            return documents
        except Exception as e:
            print(f"❌ Database error in find_all: {e}")
            return []
    
    def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return None
            
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
            print(f"❌ Database error in find_by_id: {e}")
        
        return None
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a document and return ID"""
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot insert into {self.collection_name}")
            return ""
            
        try:
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Database error in insert_one: {e}")
            return ""
    
    def update_by_id(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        update_data['updated_at'] = datetime.utcnow()
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot update {self.collection_name}")
            return False
            
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
            print(f"❌ Database error in update_by_id: {e}")
            return False
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot delete from {self.collection_name}")
            return False
            
        try:
            if isinstance(doc_id, str) and len(doc_id) == 24:
                result = self.collection.delete_one({"_id": ObjectId(doc_id)})
            else:
                result = self.collection.delete_one({"id": int(doc_id) if doc_id.isdigit() else doc_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Database error in delete_by_id: {e}")
            return False

class CameraModel(BaseModel):
    """Camera model for managing IP cameras and webcams"""
    
    def __init__(self):
        super().__init__(CAMERAS_COLLECTION)
    
    def create_camera(self, name: str, location: str, url: str, camera_type: str, 
                     username: str = "", password: str = "", enabled: bool = True, 
                     ai_mode: str = "both") -> str:
        """Create a new camera
        
        Args:
            ai_mode: AI detection mode - 'lbph' (face recognition only), 
                    'yolov9' (activity detection only), or 'both' (default)
        """
        camera_data = {
            'name': name,
            'location': location,
            'url': url,
            'type': camera_type,
            'username': username,
            'password': password,
            'enabled': enabled,
            'status': 'online',
            'last_seen': datetime.utcnow(),
            'recording': False,
            'motion_detection': True,
            'ai_detection': True,
            'ai_mode': ai_mode  # 'lbph', 'yolov9', or 'both'
        }
        
        return self.insert_one(camera_data)
    
    def update_camera(self, camera_id: str, update_data: Dict[str, Any]) -> bool:
        """Update camera with provided data"""
        return self.update_by_id(camera_id, update_data)
    
    def get_online_cameras(self) -> List[Dict[str, Any]]:
        """Get all online cameras"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return []
            
        try:
            cameras = list(self.collection.find({"status": "online"}))
            for camera in cameras:
                if '_id' in camera:
                    camera['id'] = str(camera['_id'])
                    del camera['_id']
            return cameras
        except Exception as e:
            print(f"❌ Database error in get_online_cameras: {e}")
            return []
    
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
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot create alert")
            return ""
            
        try:
            alert_data['created_at'] = datetime.utcnow()
            alert_data['updated_at'] = datetime.utcnow()
            result = self.collection.insert_one(alert_data)
            print(f"💾 Alert saved to MongoDB: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ MongoDB save failed: {e}")
            return ""
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot get alerts")
            return []
            
        try:
            alerts = list(self.collection.find().sort("timestamp", -1).limit(limit))
            for alert in alerts:
                if '_id' in alert:
                    alert['id'] = str(alert['_id'])
                    del alert['_id']
            return alerts
        except Exception as e:
            print(f"❌ MongoDB query failed: {e}")
            return []
    
    def get_alerts_today(self) -> int:
        """Get count of alerts today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot count alerts")
            return 0
            
        try:
            return self.collection.count_documents({"timestamp": {"$gte": today_start}})
        except Exception as e:
            print(f"❌ MongoDB query failed: {e}")
            return 0

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
        
        return self.insert_one(log_data)
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot get logs")
            return []
            
        try:
            logs = list(self.collection.find().sort("timestamp", -1).limit(limit))
            for log in logs:
                if '_id' in log:
                    log['id'] = str(log['_id'])
                    del log['_id']
            return logs
        except Exception as e:
            print(f"❌ Database error in get_recent_logs: {e}")
            return []

# Global model instances
camera_model = CameraModel()
alert_model = AlertModel()
log_model = LogModel()