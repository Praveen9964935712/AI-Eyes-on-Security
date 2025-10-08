import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
from config.settings import *

class SuspiciousActivityModel:
    def __init__(self):
        # Initialize YOLOv9 model
        self.model_path = os.path.join(MODELS_PATH, 'yolov9c.pt')
        
        try:
            # Load pre-trained YOLOv9 model
            self.model = YOLO('yolov9c.pt')  # Will download if not present
        except Exception as e:
            print(f"Error loading YOLOv9 model: {e}")
            # Fallback to YOLOv8 if YOLOv9 is not available
            self.model = YOLO('yolov8n.pt')
        
        # Define suspicious objects and activities
        self.weapon_classes = ['knife', 'gun', 'pistol', 'rifle']
        self.person_class = 'person'
        
        # COCO class names (YOLOv8/v9 trained on COCO dataset)
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        # Behavior analysis
        self.previous_detections = {}
        self.suspicious_behaviors = []
        
    def detect(self, frame):
        """Detect suspicious activities in frame"""
        detection_result = {
            'threat_detected': False,
            'type': 'normal_activity',
            'confidence': 0,
            'description': 'Normal activity detected',
            'detections': [],
            'suspicious_objects': [],
            'person_count': 0,
            'weapon_detected': False
        }
        
        try:
            # Run YOLO detection
            results = self.model(frame, conf=DETECTION_CONFIDENCE)
            
            persons = []
            weapons = []
            all_detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection details
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        if class_id < len(self.class_names):
                            class_name = self.class_names[class_id]
                            
                            detection = {
                                'class': class_name,
                                'confidence': float(confidence),
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [(x1 + x2) / 2, (y1 + y2) / 2]
                            }
                            
                            all_detections.append(detection)
                            
                            # Check for persons
                            if class_name == 'person' and confidence > DETECTION_CONFIDENCE:
                                persons.append(detection)
                            
                            # Check for weapons
                            elif class_name in self.weapon_classes and confidence > DETECTION_CONFIDENCE:
                                weapons.append(detection)
                                detection_result['weapon_detected'] = True
            
            # Update detection result
            detection_result['person_count'] = len(persons)
            detection_result['detections'] = all_detections
            detection_result['suspicious_objects'] = weapons
            
            # Analyze for suspicious activities
            suspicious_score = self._analyze_suspicious_behavior(persons, weapons, frame)
            
            if suspicious_score > SUSPICIOUS_ACTIVITY_THRESHOLD:
                detection_result['threat_detected'] = True
                detection_result['confidence'] = suspicious_score * 100
                detection_result['type'] = self._determine_threat_type(persons, weapons)
                detection_result['description'] = self._generate_threat_description(persons, weapons)
        
        except Exception as e:
            print(f"Error in suspicious activity detection: {e}")
            detection_result['description'] = f"Detection error: {e}"
        
        return detection_result
    
    def _analyze_suspicious_behavior(self, persons, weapons, frame):
        """Analyze behavior patterns for suspicious activity"""
        suspicious_score = 0.0
        
        # Weapon detection adds significant suspicion
        if weapons:
            suspicious_score += 0.8
        
        # Multiple people in restricted areas
        if len(persons) > 3:
            suspicious_score += 0.3
        
        # Person behavior analysis
        for person in persons:
            # Check if person is moving erratically (simplified)
            person_id = self._get_person_id(person)
            current_pos = person['center']
            
            if person_id in self.previous_detections:
                prev_pos = self.previous_detections[person_id]['center']
                movement_distance = np.sqrt((current_pos[0] - prev_pos[0])**2 + 
                                          (current_pos[1] - prev_pos[1])**2)
                
                # Rapid movement might indicate panic or aggressive behavior
                if movement_distance > 50:  # pixels
                    suspicious_score += 0.2
            
            self.previous_detections[person_id] = person
        
        # Check for person-weapon proximity
        for person in persons:
            for weapon in weapons:
                person_center = person['center']
                weapon_center = weapon['center']
                distance = np.sqrt((person_center[0] - weapon_center[0])**2 + 
                                 (person_center[1] - weapon_center[1])**2)
                
                if distance < 100:  # Close proximity
                    suspicious_score += 0.6
        
        return min(suspicious_score, 1.0)  # Cap at 1.0
    
    def _get_person_id(self, person):
        """Simple person ID based on position (in real implementation, use tracking)"""
        center = person['center']
        return f"{int(center[0]//50)}_{int(center[1]//50)}"
    
    def _determine_threat_type(self, persons, weapons):
        """Determine the type of threat based on detections"""
        if weapons and persons:
            return 'armed_threat'
        elif weapons:
            return 'weapon_detected'
        elif len(persons) > 3:
            return 'crowd_formation'
        else:
            return 'suspicious_activity'
    
    def _generate_threat_description(self, persons, weapons):
        """Generate human-readable threat description"""
        descriptions = []
        
        if weapons:
            weapon_types = [w['class'] for w in weapons]
            descriptions.append(f"Weapon detected: {', '.join(set(weapon_types))}")
        
        if len(persons) > 1:
            descriptions.append(f"{len(persons)} people detected")
        elif len(persons) == 1:
            descriptions.append("1 person detected")
        
        if weapons and persons:
            descriptions.append("Armed individual detected - immediate alert required")
        
        return ". ".join(descriptions) if descriptions else "Suspicious activity detected"
    
    def get_detection_frame(self, frame):
        """Get frame with detection annotations"""
        annotated_frame = frame.copy()
        
        try:
            results = self.model(frame, conf=DETECTION_CONFIDENCE)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection details
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        if class_id < len(self.class_names):
                            class_name = self.class_names[class_id]
                            
                            # Color coding based on object type
                            if class_name == 'person':
                                color = (0, 255, 0)  # Green for person
                            elif class_name in self.weapon_classes:
                                color = (0, 0, 255)  # Red for weapons
                            else:
                                color = (255, 255, 0)  # Yellow for other objects
                            
                            # Draw bounding box
                            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            
                            # Add label
                            label = f"{class_name}: {confidence:.2f}"
                            cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        except Exception as e:
            print(f"Error in annotation: {e}")
        
        return annotated_frame
    
    def reset_tracking(self):
        """Reset behavior tracking (useful when switching cameras)"""
        self.previous_detections = {}
        self.suspicious_behaviors = []