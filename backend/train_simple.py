"""
LBPH Face Recognition Training - Simple Version (No Emojis)
"""

import cv2
import os
import numpy as np
import pickle

class LBPHTrainer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8, threshold=65.0
        )
        self.label_map = {}
        self.training_data = []
        self.labels = []
        
    def load_training_data(self, known_faces_dir='data/known_faces'):
        print("\n" + "="*70)
        print("LBPH FACE RECOGNITION TRAINING")
        print("="*70)
        print(f"Loading training data from: {known_faces_dir}\n")
        
        label_id = 0
        total_faces = 0
        
        for person_folder in os.listdir(known_faces_dir):
            person_path = os.path.join(known_faces_dir, person_folder)
            
            if not os.path.isdir(person_path) or person_folder.startswith('.'):
                continue
            
            self.label_map[label_id] = person_folder
            person_face_count = 0
            
            print(f"Loading images for: {person_folder}")
            
            for image_file in os.listdir(person_path):
                if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(person_path, image_file)
                image = cv2.imread(image_path)
                
                if image is None:
                    print(f"   [WARN] Could not read: {image_file}")
                    continue
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                
                if len(faces) == 0:
                    print(f"   [WARN] No face detected in: {image_file}")
                    continue
                
                if len(faces) > 1:
                    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
                
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                self.training_data.append(face_roi)
                self.labels.append(label_id)
                person_face_count += 1
            
            total_faces += person_face_count
            print(f"   [OK] Loaded {person_face_count} face images")
            label_id += 1
        
        print(f"\nTraining Summary:")
        print(f"   * Total persons: {len(self.label_map)}")
        print(f"   * Total face images: {total_faces}")
        print(f"   * Average images per person: {total_faces / len(self.label_map) if self.label_map else 0:.1f}")
        
        return len(self.training_data) > 0
    
    def train_model(self):
        if len(self.training_data) == 0:
            print("\n[ERROR] No training data available!")
            return False
        
        print(f"\nTraining LBPH model with {len(self.training_data)} face images...")
        self.face_recognizer.train(self.training_data, np.array(self.labels))
        print("[OK] Training completed successfully!")
        return True
    
    def save_model(self, model_path='surveillance/lbph_model.xml',
                   label_map_path='surveillance/lbph_label_map.pkl'):
        print(f"\nSaving trained model...")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model using save()
        self.face_recognizer.save(model_path)
        print(f"   [OK] Model saved to: {model_path}")
        
        # Save label map
        with open(label_map_path, 'wb') as f:
            pickle.dump(self.label_map, f)
        print(f"   [OK] Label map saved to: {label_map_path}")
        
        print(f"\nAuthorized Personnel:")
        for label_id, person_name in self.label_map.items():
            image_count = self.labels.count(label_id)
            print(f"   * {person_name}: {image_count} training images")


if __name__ == "__main__":
    trainer = LBPHTrainer()
    
    if not trainer.load_training_data():
        print("\n[ERROR] Failed to load training data!")
        exit(1)
    
    if not trainer.train_model():
        print("\n[ERROR] Training failed!")
        exit(1)
    
    trainer.save_model()
    
    print("\n" + "="*70)
    print("[SUCCESS] LBPH FACE RECOGNITION MODEL TRAINED!")
    print("="*70)
    print("\nNext Steps:")
    print("   1. Run validation: python validate_simple.py <folder_path>")
    print("   2. Deploy in LBPH-only camera mode")
    print("\nThreshold Settings:")
    print("   * Authorized: confidence < 65")
    print("   * Uncertain: confidence 65-70")
    print("   * Intruder: confidence > 70")
    print("="*70 + "\n")
