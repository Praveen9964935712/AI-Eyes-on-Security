"""
LBPH Face Recognition Model Tester
Interactive testing with webcam or test images
"""

import cv2
import numpy as np
import os
from pathlib import Path
import pickle
import sys

class LBPHModelTester:
    def __init__(self):
        # Initialize LBPH recognizer with same parameters as training
        # NOTE: threshold parameter is NOT used for recognition decision
        # It's the max distance - we check confidence manually instead
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2,
            neighbors=16,
            grid_x=8,
            grid_y=8
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
        print("\n" + "="*70)
        print("LOADING AND TRAINING LBPH MODEL")
        print("="*70)
        
        known_faces_path = Path(known_faces_dir)
        if not known_faces_path.exists():
            print(f"[ERROR] Training directory not found: {known_faces_dir}")
            return False
        
        # Load training images
        current_label = 0
        person_dirs = [d for d in known_faces_path.iterdir() if d.is_dir()]
        
        for person_dir in person_dirs:
            person_name = person_dir.name
            print(f"\nLoading: {person_name}")
            
            image_files = list(person_dir.glob('*.jpg')) + list(person_dir.glob('*.png'))
            faces_loaded = 0
            
            for img_path in image_files:
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
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
                print(f"  [OK] {faces_loaded} images")
                current_label += 1
        
        if len(self.training_data) == 0:
            print("\n[ERROR] No training data loaded!")
            return False
        
        # Train the model
        print(f"\nTraining model with {len(self.training_data)} face images...")
        self.face_recognizer.train(self.training_data, np.array(self.labels))
        self.is_trained = True
        
        print("[OK] Model trained successfully!")
        print("\nAuthorized Personnel:")
        for label, name in self.label_map.items():
            count = self.labels.count(label)
            print(f"  {count:2d} images - {name}")
        
        return True
    
    def get_recognition_status(self, confidence):
        """Determine recognition status based on confidence threshold"""
        # LBPH confidence: Lower = Better match
        # Adjusted thresholds for live testing (more lenient)
        if confidence <= 80:
            return "AUTHORIZED", (0, 255, 0)  # Green
        elif confidence <= 100:
            return "UNCERTAIN", (0, 165, 255)  # Orange
        else:
            return "INTRUDER", (0, 0, 255)  # Red
    
    def test_with_webcam(self):
        """Test model with live webcam feed"""
        if not self.is_trained:
            print("[ERROR] Model not trained!")
            return
        
        print("\n" + "="*70)
        print("WEBCAM TEST MODE")
        print("="*70)
        print("\nInstructions:")
        print("  - Position your face in front of the camera")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save screenshot")
        print("\nStarting webcam...")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("[ERROR] Could not open webcam!")
            return
        
        screenshot_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame")
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face ROI
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (100, 100))
                
                # Recognize face
                label, confidence = self.face_recognizer.predict(face_resized)
                
                # Get status and color
                status, color = self.get_recognition_status(confidence)
                
                # Get person name
                if confidence <= 100:
                    person_name = self.label_map.get(label, "Unknown")
                else:
                    person_name = "Unknown"
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Prepare text
                if status == "AUTHORIZED":
                    text = f"{status}: {person_name}"
                    conf_text = f"Confidence: {confidence:.1f}"
                elif status == "UNCERTAIN":
                    text = f"{status}: {person_name}?"
                    conf_text = f"Confidence: {confidence:.1f}"
                else:
                    text = f"{status}: {person_name}"
                    conf_text = f"Confidence: {confidence:.1f}"
                
                # Draw text background
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x, y-35), (x+text_size[0]+10, y), color, -1)
                
                # Draw text
                cv2.putText(frame, text, (x+5, y-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, conf_text, (x+5, y-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display info overlay
            info_text = f"Faces: {len(faces)} | Press 'q' to quit, 's' to screenshot"
            cv2.putText(frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('LBPH Face Recognition Test', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n[INFO] Exiting...")
                break
            elif key == ord('s'):
                screenshot_count += 1
                filename = f'test_screenshot_{screenshot_count}.jpg'
                cv2.imwrite(filename, frame)
                print(f"[INFO] Screenshot saved: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Webcam test completed")
    
    def test_with_image(self, image_path):
        """Test model with a single image"""
        if not self.is_trained:
            print("[ERROR] Model not trained!")
            return
        
        print("\n" + "="*70)
        print(f"TESTING IMAGE: {image_path}")
        print("="*70)
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"[ERROR] Could not read image: {image_path}")
            return
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        print(f"\nFaces detected: {len(faces)}")
        
        if len(faces) == 0:
            print("[WARNING] No faces detected in image!")
            cv2.imshow('Test Image - No Face Detected', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return
        
        # Process each detected face
        for idx, (x, y, w, h) in enumerate(faces, 1):
            # Extract face ROI
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face_resized)
            
            # Get status and color
            status, color = self.get_recognition_status(confidence)
            
            # Get person name
            if confidence <= 100:
                person_name = self.label_map.get(label, "Unknown")
            else:
                person_name = "Unknown"
            
            # Print results
            print(f"\nFace #{idx}:")
            print(f"  Status: {status}")
            print(f"  Person: {person_name}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Position: ({x}, {y}), Size: {w}x{h}")
            
            # Draw rectangle around face
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
            
            # Prepare text
            if status == "AUTHORIZED":
                text = f"{status}: {person_name}"
            elif status == "UNCERTAIN":
                text = f"{status}: {person_name}?"
            else:
                text = f"{status}"
            
            # Draw text background
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.rectangle(img, (x, y-40), (x+text_size[0]+10, y), color, -1)
            
            # Draw text
            cv2.putText(img, text, (x+5, y-25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(img, f"Conf: {confidence:.1f}", (x+5, y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show result
        cv2.imshow('Test Result - Press any key to close', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def test_with_directory(self, directory_path):
        """Test model with all images in a directory"""
        if not self.is_trained:
            print("[ERROR] Model not trained!")
            return
        
        print("\n" + "="*70)
        print(f"BATCH TESTING DIRECTORY: {directory_path}")
        print("="*70)
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            print(f"[ERROR] Directory not found: {directory_path}")
            return
        
        # Get all image files
        image_files = list(dir_path.glob('*.jpg')) + list(dir_path.glob('*.png'))
        print(f"\nFound {len(image_files)} images")
        
        # Statistics
        stats = {
            'total': 0,
            'faces_detected': 0,
            'authorized': 0,
            'uncertain': 0,
            'intruder': 0,
            'no_face': 0
        }
        
        print("\nProcessing images (press any key to continue, 'q' to quit)...\n")
        
        for img_path in image_files:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            stats['total'] += 1
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                stats['no_face'] += 1
                print(f"[{stats['total']:3d}] {img_path.name[:50]:50s} - No face")
                continue
            
            stats['faces_detected'] += 1
            
            # Process first face
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face_resized)
            status, color = self.get_recognition_status(confidence)
            
            if confidence <= 80:
                stats['authorized'] += 1
                person_name = self.label_map.get(label, "Unknown")
                result = f"AUTHORIZED - {person_name:20s} (conf: {confidence:.1f})"
            elif confidence <= 100:
                stats['uncertain'] += 1
                person_name = self.label_map.get(label, "Unknown")
                result = f"UNCERTAIN  - {person_name:20s} (conf: {confidence:.1f})"
            else:
                stats['intruder'] += 1
                result = f"INTRUDER   - Unknown person (conf: {confidence:.1f})"
            
            print(f"[{stats['total']:3d}] {img_path.name[:50]:50s} - {result}")
            
            # Draw results on image
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
            cv2.putText(img, result[:30], (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Show image
            cv2.imshow('Batch Test - Press any key for next, q to quit', img)
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                print("\n[INFO] Batch test interrupted by user")
                break
        
        cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "="*70)
        print("BATCH TEST SUMMARY")
        print("="*70)
        print(f"\nTotal images: {stats['total']}")
        print(f"Faces detected: {stats['faces_detected']}")
        print(f"No face detected: {stats['no_face']}")
        
        if stats['faces_detected'] > 0:
            print(f"\nRecognition Results:")
            print(f"  AUTHORIZED (0-65):  {stats['authorized']:3d} ({stats['authorized']/stats['faces_detected']*100:.1f}%)")
            print(f"  UNCERTAIN (65-70):  {stats['uncertain']:3d} ({stats['uncertain']/stats['faces_detected']*100:.1f}%)")
            print(f"  INTRUDER (70+):     {stats['intruder']:3d} ({stats['intruder']/stats['faces_detected']*100:.1f}%)")


def print_menu():
    """Print the main menu"""
    print("\n" + "="*70)
    print("LBPH FACE RECOGNITION MODEL TESTER")
    print("="*70)
    print("\nTest Options:")
    print("  1. Test with Webcam (Live)")
    print("  2. Test with Single Image")
    print("  3. Test with Directory (Batch)")
    print("  4. Exit")
    print("="*70)


def main():
    print("\n" + "="*70)
    print("INITIALIZING LBPH FACE RECOGNITION TESTER")
    print("="*70)
    
    tester = LBPHModelTester()
    
    # Load and train the model
    if not tester.load_and_train('data/known_faces'):
        print("\n[ERROR] Failed to load and train model!")
        return
    
    # Main menu loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            tester.test_with_webcam()
        
        elif choice == '2':
            image_path = input("\nEnter image path (or press Enter for validation image): ").strip()
            if not image_path:
                # Use a validation image
                validation_dir = Path('../data/validation_images')
                if validation_dir.exists():
                    images = list(validation_dir.glob('*.jpg'))
                    if images:
                        image_path = str(images[0])
                        print(f"Using: {image_path}")
                    else:
                        print("[ERROR] No validation images found!")
                        continue
                else:
                    print("[ERROR] Validation directory not found!")
                    continue
            
            if os.path.exists(image_path):
                tester.test_with_image(image_path)
            else:
                print(f"[ERROR] File not found: {image_path}")
        
        elif choice == '3':
            directory_path = input("\nEnter directory path (or press Enter for validation_images): ").strip()
            if not directory_path:
                directory_path = '../data/validation_images'
                print(f"Using: {directory_path}")
            
            tester.test_with_directory(directory_path)
        
        elif choice == '4':
            print("\n[INFO] Exiting tester...")
            break
        
        else:
            print("\n[ERROR] Invalid choice! Please enter 1-4")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
