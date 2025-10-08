import cv2
import numpy as np
import os
from datetime import datetime
import pickle
from config.settings import *

class FaceRecognitionModel:
    def __init__(self):
        # Initialize LBPH face recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Known faces and labels
        self.known_faces = {}
        self.known_labels = {}
        self.label_counter = 0
        
        # Load existing model if available
        self.model_path = os.path.join(MODELS_PATH, 'lbph_model.xml')
        self.labels_path = os.path.join(MODELS_PATH, 'face_labels.pkl')
        
        self._load_known_faces()
        self._load_model()
    
    def _load_known_faces(self):
        """Load known faces from the known_faces directory"""
        known_faces_dir = KNOWN_FACES_PATH
        if not os.path.exists(known_faces_dir):
            os.makedirs(known_faces_dir)
            return
        
        faces = []
        labels = []
        
        for person_name in os.listdir(known_faces_dir):
            person_dir = os.path.join(known_faces_dir, person_name)
            if os.path.isdir(person_dir):
                # Assign label to person
                if person_name not in self.known_labels:
                    self.known_labels[person_name] = self.label_counter
                    self.label_counter += 1
                
                person_label = self.known_labels[person_name]
                
                # Load all images for this person
                for image_file in os.listdir(person_dir):
                    if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(person_dir, image_file)
                        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        
                        if image is not None:
                            # Detect face in the image
                            face_detected = self.face_cascade.detectMultiScale(
                                image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                            )
                            
                            for (x, y, w, h) in face_detected:
                                face_roi = image[y:y+h, x:x+w]
                                # Resize face to standard size
                                face_roi = cv2.resize(face_roi, (100, 100))
                                faces.append(face_roi)
                                labels.append(person_label)
        
        if faces:
            # Train the recognizer
            self.recognizer.train(faces, np.array(labels))
            print(f"Trained face recognizer with {len(faces)} faces for {len(self.known_labels)} people")
            
            # Save the model
            self._save_model()
    
    def _load_model(self):
        """Load existing trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.labels_path):
                self.recognizer.read(self.model_path)
                with open(self.labels_path, 'rb') as f:
                    self.known_labels = pickle.load(f)
                print("Loaded existing face recognition model")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def _save_model(self):
        """Save trained model"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(MODELS_PATH, exist_ok=True)
            
            self.recognizer.write(self.model_path)
            with open(self.labels_path, 'wb') as f:
                pickle.dump(self.known_labels, f)
            print("Saved face recognition model")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def add_known_person(self, name, images):
        """Add a new known person to the system"""
        person_dir = os.path.join(KNOWN_FACES_PATH, name)
        os.makedirs(person_dir, exist_ok=True)
        
        # Save images
        for i, image in enumerate(images):
            image_path = os.path.join(person_dir, f"{name}_{i+1}.jpg")
            cv2.imwrite(image_path, image)
        
        # Retrain the model
        self._load_known_faces()
        
        return True
    
    def detect(self, frame):
        """Detect faces in frame and identify if they are known or unknown"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        detection_result = {
            'threat_detected': False,
            'type': 'unknown_person',
            'confidence': 0,
            'description': 'No faces detected',
            'faces_detected': len(faces),
            'unknown_faces': 0,
            'known_faces': []
        }
        
        unknown_faces = 0
        known_faces_list = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.recognizer.predict(face_roi)
            
            # LBPH confidence: lower values mean better match
            # We need to invert this logic for our threshold
            confidence_percentage = max(0, 100 - confidence)
            
            if confidence < 100:  # LBPH threshold (lower is better)
                # Known person detected
                person_name = None
                for name, person_label in self.known_labels.items():
                    if person_label == label:
                        person_name = name
                        break
                
                if person_name:
                    known_faces_list.append({
                        'name': person_name,
                        'confidence': confidence_percentage,
                        'bbox': (x, y, w, h)
                    })
            else:
                # Unknown person detected
                unknown_faces += 1
        
        # Update detection result
        detection_result['unknown_faces'] = unknown_faces
        detection_result['known_faces'] = known_faces_list
        
        if unknown_faces > 0:
            detection_result['threat_detected'] = True
            detection_result['confidence'] = 95  # High confidence for unknown person
            detection_result['description'] = f"Unknown person detected at farm entrance. {unknown_faces} unrecognized face(s) found."
        elif known_faces_list:
            detection_result['description'] = f"Authorized personnel detected: {', '.join([face['name'] for face in known_faces_list])}"
        
        return detection_result
    
    def get_detection_frame(self, frame):
        """Get frame with detection annotations"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        annotated_frame = frame.copy()
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.recognizer.predict(face_roi)
            
            if confidence < 100:  # Known person
                person_name = None
                for name, person_label in self.known_labels.items():
                    if person_label == label:
                        person_name = name
                        break
                
                if person_name:
                    # Green box for known person
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f"{person_name} ({100-confidence:.1f}%)", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    # Yellow box for unrecognized but detected face
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(annotated_frame, "Unrecognized", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                # Red box for unknown person
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(annotated_frame, "UNKNOWN INTRUDER", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated_frame