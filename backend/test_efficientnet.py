"""
Test Script for EfficientNet B7 Face Recognition
Tests the model with images and live camera
"""

import cv2
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from surveillance.efficientnet_face_recognition import EfficientNetFaceRecognizer

def print_separator():
    print("=" * 70)

def test_model_loading():
    """Test 1: Check if model loads successfully"""
    print_separator()
    print("TEST 1: Model Loading")
    print_separator()
    
    try:
        recognizer = EfficientNetFaceRecognizer()
        
        if recognizer.is_trained:
            print("✅ Model loaded successfully!")
            print(f"✅ Model is trained: {recognizer.is_trained}")
            
            # Get authorized persons
            authorized = recognizer.get_authorized_persons()
            print(f"✅ Authorized persons ({len(authorized)}):")
            for i, person in enumerate(authorized, 1):
                print(f"   {i}. {person}")
            
            return recognizer
        else:
            print("❌ Model is not trained!")
            return None
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_face_detection(recognizer):
    """Test 2: Test face detection with webcam"""
    print_separator()
    print("TEST 2: Face Detection (Press 'q' to skip)")
    print_separator()
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return False
        
        print("✅ Webcam opened successfully")
        print("📸 Testing face detection...")
        print("   Press 'q' to stop test")
        
        frame_count = 0
        faces_detected = 0
        
        while frame_count < 100:  # Test for 100 frames max
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            face_boxes = recognizer.detect_faces(frame)
            
            if len(face_boxes) > 0:
                faces_detected += 1
                print(f"✅ Frame {frame_count}: Detected {len(face_boxes)} face(s)")
                
                # Draw boxes
                for (x, y, w, h) in face_boxes:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Face Detected", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('Face Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Results:")
        print(f"   Frames processed: {frame_count}")
        print(f"   Frames with faces: {faces_detected}")
        print(f"   Detection rate: {(faces_detected/frame_count*100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in face detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_face_recognition(recognizer):
    """Test 3: Test face recognition with webcam"""
    print_separator()
    print("TEST 3: Face Recognition (Press 'q' to stop)")
    print_separator()
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return False
        
        print("✅ Webcam opened successfully")
        print("🎯 Testing face recognition...")
        print(f"   Authorized persons: {', '.join(recognizer.get_authorized_persons())}")
        print("   Press 'q' to stop test")
        print()
        
        recognition_results = {}
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Recognize faces
            results = recognizer.recognize_faces(frame)
            
            # Draw results
            for result in results:
                name = result['name']
                bbox = result['bbox']
                is_authorized = result['is_authorized']
                confidence = result['confidence']
                
                x, y, w, h = bbox
                
                # Color based on authorization
                color = (0, 255, 0) if is_authorized else (0, 0, 255)
                
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Draw label
                label = f"{name} ({confidence:.0%})" if is_authorized else "INTRUDER"
                cv2.rectangle(frame, (x, y-30), (x+w, y), color, -1)
                cv2.putText(frame, label, (x+5, y-10), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Track results
                if name not in recognition_results:
                    recognition_results[name] = 0
                recognition_results[name] += 1
                
                # Print recognition
                status = "✅ AUTHORIZED" if is_authorized else "🚨 INTRUDER"
                print(f"Frame {frame_count}: {status} - {name} (confidence: {confidence:.0%})")
            
            # Display frame
            cv2.imshow('EfficientNet B7 Face Recognition Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Recognition Results:")
        print(f"   Total frames: {frame_count}")
        print(f"   Recognized persons:")
        for person, count in recognition_results.items():
            print(f"      {person}: {count} times")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in face recognition: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_image(recognizer):
    """Test 4: Test with a sample image"""
    print_separator()
    print("TEST 4: Image Recognition")
    print_separator()
    
    # Check for test images
    test_dirs = [
        Path("data/known_faces"),
        Path("../data/known_faces")
    ]
    
    for test_dir in test_dirs:
        if test_dir.exists():
            print(f"✅ Found test directory: {test_dir}")
            
            # Get first image from first person folder
            for person_folder in test_dir.iterdir():
                if person_folder.is_dir():
                    for img_file in person_folder.glob("*.jpg"):
                        print(f"📸 Testing with: {img_file.name} from {person_folder.name}")
                        
                        # Load image
                        image = cv2.imread(str(img_file))
                        if image is None:
                            continue
                        
                        # Recognize
                        results = recognizer.recognize_faces(image)
                        
                        if len(results) > 0:
                            for result in results:
                                print(f"   Detected: {result['name']}")
                                print(f"   Authorized: {result['is_authorized']}")
                                print(f"   Confidence: {result['confidence']:.2%}")
                                
                                # Draw on image
                                x, y, w, h = result['bbox']
                                color = (0, 255, 0) if result['is_authorized'] else (0, 0, 255)
                                cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
                                cv2.putText(image, result['name'], (x, y-10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                            
                            # Show result
                            cv2.imshow('Test Result', image)
                            print("   Press any key to continue...")
                            cv2.waitKey(0)
                            cv2.destroyAllWindows()
                            
                            return True
                        else:
                            print("   ⚠️ No faces detected in image")
                        
                        return True
            
    print("⚠️ No test images found in data/known_faces/")
    return False

def main():
    """Main test runner"""
    print("\n" * 2)
    print("=" * 70)
    print(" " * 15 + "EFFICIENTNET B7 TEST SUITE")
    print("=" * 70)
    print()
    
    # Test 1: Load model
    recognizer = test_model_loading()
    if not recognizer:
        print("\n❌ Cannot continue without loaded model")
        return
    
    print("\n✅ Model is ready for testing!")
    print()
    
    # Menu
    while True:
        print_separator()
        print("TESTING OPTIONS:")
        print_separator()
        print("1. Test Face Detection (webcam)")
        print("2. Test Face Recognition (webcam)")
        print("3. Test with Sample Image")
        print("4. Run All Tests")
        print("5. Exit")
        print_separator()
        
        choice = input("Select test (1-5): ").strip()
        
        if choice == '1':
            test_face_detection(recognizer)
        elif choice == '2':
            test_face_recognition(recognizer)
        elif choice == '3':
            test_with_image(recognizer)
        elif choice == '4':
            test_face_detection(recognizer)
            test_face_recognition(recognizer)
            test_with_image(recognizer)
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5")
        
        print("\n")

if __name__ == "__main__":
    main()
