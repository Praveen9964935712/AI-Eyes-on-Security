"""
LBPH Face Recognition Validation (In-Memory)
Workaround for OpenCV model save bug - trains model in memory then validates
"""

import cv2
import numpy as np
import os
from pathlib import Path
import pickle

class LBPHValidator:
    def __init__(self):
        # Initialize LBPH recognizer with same parameters as training
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2,
            neighbors=16,
            grid_x=8,
            grid_y=8,
            threshold=65.0
        )
        
        # Initialize Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.training_data = []
        self.labels = []
        self.label_map = {}
        self.name_map = {}
        self.is_trained = False
    
    def load_and_train(self, known_faces_dir='data/known_faces'):
        """Load training data and train the model in memory"""
        print("\n" + "="*60)
        print("STEP 1: LOADING TRAINING DATA")
        print("="*60)
        
        known_faces_path = Path(known_faces_dir)
        if not known_faces_path.exists():
            print(f"[ERROR] Training directory not found: {known_faces_dir}")
            return False
        
        # Load training images
        current_label = 0
        person_dirs = [d for d in known_faces_path.iterdir() if d.is_dir()]
        
        for person_dir in person_dirs:
            person_name = person_dir.name
            print(f"\nLoading images for: {person_name}")
            
            image_files = list(person_dir.glob('*.jpg')) + list(person_dir.glob('*.png'))
            faces_loaded = 0
            
            for img_path in image_files:
                # Read image
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Process first detected face
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (100, 100))
                    
                    self.training_data.append(face_resized)
                    self.labels.append(current_label)
                    faces_loaded += 1
            
            if faces_loaded > 0:
                self.label_map[current_label] = person_name
                self.name_map[person_name] = current_label
                print(f"  [OK] Loaded {faces_loaded} face images")
                current_label += 1
            else:
                print(f"  [WARNING] No faces detected")
        
        if len(self.training_data) == 0:
            print("\n[ERROR] No training data loaded!")
            return False
        
        # Train the model
        print("\n" + "="*60)
        print(f"STEP 2: TRAINING MODEL ({len(self.training_data)} faces)")
        print("="*60)
        
        self.face_recognizer.train(self.training_data, np.array(self.labels))
        self.is_trained = True
        
        print("[OK] Model trained successfully in memory!")
        print("\nAuthorized Personnel:")
        for label, name in self.label_map.items():
            count = self.labels.count(label)
            print(f"  * {name}: {count} training images")
        
        return True
    
    def validate(self, validation_dir='../data/validation_images'):
        """Validate the trained model on validation images"""
        if not self.is_trained:
            print("[ERROR] Model not trained!")
            return
        
        print("\n" + "="*60)
        print("STEP 3: VALIDATION ON TEST IMAGES")
        print("="*60)
        
        validation_path = Path(validation_dir)
        if not validation_path.exists():
            print(f"[ERROR] Validation directory not found: {validation_dir}")
            return
        
        # Get all validation images
        image_files = list(validation_path.glob('*.jpg')) + list(validation_path.glob('*.png'))
        print(f"\nFound {len(image_files)} validation images")
        
        # Validation statistics
        stats = {
            'total': 0,
            'faces_detected': 0,
            'authorized': 0,
            'uncertain': 0,
            'intruder': 0,
            'by_person': {}
        }
        
        print("\nProcessing validation images...\n")
        
        for idx, img_path in enumerate(image_files, 1):
            # Read image
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            stats['total'] += 1
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                print(f"[{idx:3d}] {img_path.name[:40]:40s} - No face detected")
                continue
            
            stats['faces_detected'] += 1
            
            # Process first detected face
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face_resized)
            
            # Determine status based on confidence
            if confidence <= 65:
                status = "AUTHORIZED"
                stats['authorized'] += 1
                person_name = self.label_map.get(label, "Unknown")
                stats['by_person'][person_name] = stats['by_person'].get(person_name, 0) + 1
                result = f"{status:12s} - {person_name:20s} (conf: {confidence:.1f})"
            elif confidence <= 70:
                status = "UNCERTAIN"
                stats['uncertain'] += 1
                person_name = self.label_map.get(label, "Unknown")
                result = f"{status:12s} - {person_name:20s} (conf: {confidence:.1f})"
            else:
                status = "INTRUDER"
                stats['intruder'] += 1
                result = f"{status:12s} - Unknown person (conf: {confidence:.1f})"
            
            print(f"[{idx:3d}] {img_path.name[:40]:40s} - {result}")
        
        # Print validation summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"\nTotal images processed: {stats['total']}")
        print(f"Faces detected: {stats['faces_detected']}")
        print(f"No face detected: {stats['total'] - stats['faces_detected']}")
        
        if stats['faces_detected'] > 0:
            print(f"\nRecognition Results:")
            print(f"  AUTHORIZED (0-65):  {stats['authorized']:3d} ({stats['authorized']/stats['faces_detected']*100:.1f}%)")
            print(f"  UNCERTAIN (65-70):  {stats['uncertain']:3d} ({stats['uncertain']/stats['faces_detected']*100:.1f}%)")
            print(f"  INTRUDER (70+):     {stats['intruder']:3d} ({stats['intruder']/stats['faces_detected']*100:.1f}%)")
            
            if stats['by_person']:
                print(f"\nRecognized Persons:")
                for person, count in sorted(stats['by_person'].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {person}: {count} images")
        
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)


def main():
    print("\n" + "="*60)
    print("LBPH FACE RECOGNITION VALIDATION (IN-MEMORY)")
    print("="*60)
    print("\nThis script trains the LBPH model in memory and validates it")
    print("on the validation images - working around OpenCV save bug.\n")
    
    validator = LBPHValidator()
    
    # Train the model
    if validator.load_and_train('data/known_faces'):
        # Validate the model
        validator.validate('../data/validation_images')
    else:
        print("\n[ERROR] Training failed!")


if __name__ == "__main__":
    main()
