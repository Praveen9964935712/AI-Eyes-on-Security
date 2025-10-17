"""
LBPH Face Recognition - Simple Validation Script (No Emojis)
"""

import cv2
import os
import sys
import pickle
import numpy as np
from pathlib import Path

# Set UTF-8 encoding for Windows
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class LBPHValidator:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load model
        print("\n[LOADING MODEL]")
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        model_path = 'surveillance/lbph_model.xml'
        self.face_recognizer.read(model_path)
        print(f"Model loaded: {model_path}")
        
        # Load label map
        with open('surveillance/lbph_label_map.pkl', 'rb') as f:
            self.label_map = pickle.load(f)
        
        print(f"Authorized persons: {len(self.label_map)}")
        for label_id, name in self.label_map.items():
            print(f"  - {name}")
    
    def validate_folder(self, folder_path):
        print(f"\n[BATCH VALIDATION]: {folder_path}\n")
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(Path(folder_path).glob(ext))
        
        print(f"Found {len(image_files)} images\n")
        
        authorized_count = 0
        intruder_count = 0
        uncertain_count = 0
        no_face_count = 0
        
        for i, img_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] {img_path.name}")
            
            # Read image
            image = cv2.imread(str(img_path))
            if image is None:
                print("  ERROR: Could not read image\n")
                continue
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            if len(faces) == 0:
                print("  NO FACE DETECTED\n")
                no_face_count += 1
                continue
            
            # Process first face
            x, y, w, h = faces[0]
            face_roi = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
            
            # Predict
            label, confidence = self.face_recognizer.predict(face_roi)
            person_name = self.label_map.get(label, "Unknown")
            
            if confidence < 65:
                print(f"  [AUTHORIZED] {person_name} (confidence: {confidence:.2f})")
                authorized_count += 1
            elif confidence < 70:
                print(f"  [UNCERTAIN] {person_name} (confidence: {confidence:.2f})")
                uncertain_count += 1
            else:
                print(f"  [INTRUDER] Unknown person detected! (confidence: {confidence:.2f})")
                intruder_count += 1
            print()
        
        # Summary
        print("="*70)
        print("[VALIDATION SUMMARY]")
        print("="*70)
        print(f"Total images: {len(image_files)}")
        print(f"Faces detected: {len(image_files) - no_face_count}")
        print(f"No face detected: {no_face_count}")
        print(f"\n[AUTHORIZED]: {authorized_count}")
        print(f"[UNCERTAIN]: {uncertain_count}")
        print(f"[INTRUDERS]: {intruder_count}")
        
        if intruder_count > 0:
            print(f"\n[WARNING] {intruder_count} unauthorized access attempts detected!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_simple.py <folder_path>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    try:
        validator = LBPHValidator()
        validator.validate_folder(path)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
