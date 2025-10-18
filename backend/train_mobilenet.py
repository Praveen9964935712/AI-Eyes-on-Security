"""
Train MobileNetV2 Face Recognition Model
(Smaller model, works with ImageNet weights, perfect for small datasets)
"""

import sys
from pathlib import Path

# Add ai_models to path
current_dir = Path(__file__).parent
ai_models_path = current_dir / "ai_models" / "face_recognition"
sys.path.insert(0, str(ai_models_path))

from mobilenet_face_recognition import MobileNetFaceRecognitionSystem

def main():
    print("=" * 80)
    print("TRAINING MOBILENETV2 FACE RECOGNITION MODEL")
    print("=" * 80)
    print()
    
    # Initialize
    recognizer = MobileNetFaceRecognitionSystem()
    
    # Train
    known_faces_dir = current_dir.parent / "data" / "known_faces"
    print(f"Training with data from: {known_faces_dir}")
    
    success = recognizer.train_with_authorized_faces(str(known_faces_dir))
    
    if success:
        # Save model
        output_path = str(ai_models_path / "mobilenet_face_model")
        print(f"\n💾 Saving model to: {output_path}")
        recognizer.save_model(output_path)
        
        print("\n" + "=" * 80)
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n🎯 The model should now recognize your authorized persons correctly!")
        print(f"   Authorized: {', '.join(recognizer.authorized_persons)}")
    else:
        print("\n❌ Training failed")

if __name__ == "__main__":
    main()
