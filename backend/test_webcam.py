"""
Webcam Test for MobileNetV2 Face Recognition
Real-time face recognition using your laptop webcam
"""

import sys
from pathlib import Path
import cv2
import time

# Add ai_models to path
current_dir = Path(__file__).parent
ai_models_path = current_dir / "ai_models" / "face_recognition"
sys.path.insert(0, str(ai_models_path))

from mobilenet_face_recognition import MobileNetFaceRecognitionSystem

def main():
    print("=" * 80)
    print("WEBCAM TEST - MOBILENETV2 FACE RECOGNITION")
    print("=" * 80)
    print()
    
    # Load model
    print("1. Loading MobileNetV2 v2 model (with Unknown class)...")
    recognizer = MobileNetFaceRecognitionSystem()
    model_path = str(ai_models_path / "mobilenet_face_model_v2")
    
    if not recognizer.load_model(model_path):
        print("❌ Failed to load model!")
        return
    
    print(f"✅ Model loaded successfully!")
    print(f"✅ Authorized persons: {', '.join(recognizer.authorized_persons)}")
    print()
    print(f"⚠️ Model will predict 'Unknown' class for intruders")
    
    # Open webcam
    print("2. Opening webcam...")
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    
    if not cap.isOpened():
        print("❌ Could not open webcam!")
        print("💡 Make sure your webcam is not being used by another application")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Webcam opened successfully!")
    print()
    print("=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print("✅ Green box = AUTHORIZED person (farmer_Basava, manager_prajwal, owner_rajasekhar)")
    print("🚨 Red box = INTRUDER (unknown person)")
    print()
    print("Press 'q' to quit")
    print("Press 's' to save a screenshot")
    print("=" * 80)
    print()
    
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    screenshot_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        # Mirror the frame for more natural display
        frame = cv2.flip(frame, 1)
        
        # Recognize faces
        try:
            face_names, face_locations, verification_results = recognizer.recognize_faces_in_frame(frame)
            
            # Draw results
            for (name, (top, right, bottom, left), is_authorized) in zip(face_names, face_locations, verification_results):
                # Choose color
                if is_authorized:
                    color = (0, 255, 0)  # Green for authorized
                    label = f"✅ {name}"
                    status = "AUTHORIZED"
                else:
                    color = (0, 0, 255)  # Red for intruder
                    label = "🚨 INTRUDER"
                    status = "INTRUDER"
                
                # Draw rectangle
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, top - 35), (right, top), color, cv2.FILLED)
                
                # Draw text
                cv2.putText(frame, label, (left + 6, top - 10), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
                
                # Print to console
                print(f"{'✅' if is_authorized else '🚨'} Detected: {name} - {status}")
        
        except Exception as e:
            print(f"⚠️ Recognition error: {e}")
        
        # Calculate FPS
        fps_frame_count += 1
        if time.time() - fps_start_time >= 1.0:
            fps = fps_frame_count
            fps_frame_count = 0
            fps_start_time = time.time()
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {fps}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw instructions
        cv2.putText(frame, "Press 'q' to quit | 's' to save screenshot", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('AI Eyes - MobileNetV2 Face Recognition', frame)
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n👋 Quitting...")
            break
        elif key == ord('s'):
            screenshot_count += 1
            filename = f"screenshot_{screenshot_count}_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Webcam test completed!")
    print(f"📊 Final FPS: {fps}")
    if screenshot_count > 0:
        print(f"📸 Screenshots saved: {screenshot_count}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
