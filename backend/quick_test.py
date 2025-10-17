"""
Quick LBPH Model Test - Single Image Test
Fast testing without menu navigation
"""

import cv2
import numpy as np
from pathlib import Path
import sys

class QuickLBPHTest:
    def __init__(self):
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8
        )
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.label_map = {}
        self.is_trained = False
    
    def quick_train(self):
        """Quick training from known_faces directory"""
        print("Loading training data...")
        training_data = []
        labels = []
        current_label = 0
        
        known_faces_path = Path('data/known_faces')
        for person_dir in known_faces_path.iterdir():
            if not person_dir.is_dir():
                continue
            
            person_name = person_dir.name
            for img_path in person_dir.glob('*.jpg'):
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_resized = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
                    training_data.append(face_resized)
                    labels.append(current_label)
            
            self.label_map[current_label] = person_name
            current_label += 1
        
        print(f"Training with {len(training_data)} faces...")
        self.face_recognizer.train(training_data, np.array(labels))
        self.is_trained = True
        print("Model trained!\n")
    
    def test_image(self, image_path):
        """Test a single image"""
        img = cv2.imread(image_path)
        if img is None:
            print(f"ERROR: Could not read {image_path}")
            return
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        if len(faces) == 0:
            print("No faces detected!")
            cv2.imshow('Result', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return
        
        print(f"\n{'='*60}")
        print(f"Testing: {Path(image_path).name}")
        print(f"{'='*60}\n")
        
        for idx, (x, y, w, h) in enumerate(faces, 1):
            face_resized = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
            label, confidence = self.face_recognizer.predict(face_resized)
            
            # Determine status
            if confidence <= 80:
                status = "AUTHORIZED"
                color = (0, 255, 0)
                person = self.label_map.get(label, "Unknown")
            elif confidence <= 100:
                status = "UNCERTAIN"
                color = (0, 165, 255)
                person = self.label_map.get(label, "Unknown")
            else:
                status = "INTRUDER"
                color = (0, 0, 255)
                person = "Unknown"
            
            print(f"Face #{idx}:")
            print(f"  Status:     {status}")
            print(f"  Person:     {person}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Threshold:  0-80=Auth, 80-100=Uncertain, 100+=Intruder\n")
            
            # Draw on image
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
            text = f"{status}: {person}" if status != "INTRUDER" else status
            cv2.putText(img, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(img, f"Conf: {confidence:.1f}", (x, y+h+25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Show result
        cv2.imshow('Test Result - Press any key to close', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python quick_test.py <image_path>")
        print("\nExample:")
        print("  python quick_test.py ../data/validation_images/image.jpg")
        print("  python quick_test.py test_photo.jpg")
        print("\nOr test with first validation image:")
        
        validation_dir = Path('../data/validation_images')
        if validation_dir.exists():
            images = list(validation_dir.glob('*.jpg'))
            if images:
                image_path = str(images[0])
                print(f"  Using: {image_path}\n")
            else:
                print("  No validation images found!\n")
                return
        else:
            print("  Validation directory not found!\n")
            return
    else:
        image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"ERROR: File not found: {image_path}")
        return
    
    # Quick test
    tester = QuickLBPHTest()
    tester.quick_train()
    tester.test_image(image_path)


if __name__ == "__main__":
    main()
