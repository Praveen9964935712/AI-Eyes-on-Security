"""
Retrain EfficientNet Face Recognition Model
Fixes the ImageNet weights incompatibility issue by training from scratch
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime

# Add ai_models to path
current_dir = Path(__file__).parent
ai_models_path = current_dir / "ai_models" / "face_recognition"
sys.path.insert(0, str(ai_models_path))

from improved_efficientnet_face_recognition import ImprovedEfficientNetFaceRecognitionSystem

def count_training_images(known_faces_dir):
    """Count images for each person"""
    image_counts = {}
    total_images = 0
    
    for person_dir in known_faces_dir.iterdir():
        if not person_dir.is_dir():
            continue
        
        images = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png"))
        count = len(images)
        image_counts[person_dir.name] = count
        total_images += count
    
    return image_counts, total_images

def main():
    print("=" * 80)
    print("RETRAINING EFFICIENTNET B7 FACE RECOGNITION MODEL")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check training data
    known_faces_dir = current_dir.parent / "data" / "known_faces"
    
    if not known_faces_dir.exists():
        print(f"❌ ERROR: Training data directory not found!")
        print(f"   Expected: {known_faces_dir}")
        print(f"   Please create this directory and add person folders with images")
        return False
    
    print("📁 Checking training data...")
    image_counts, total_images = count_training_images(known_faces_dir)
    
    if total_images == 0:
        print("❌ ERROR: No training images found!")
        print(f"   Add images to: {known_faces_dir}")
        print(f"   Structure: data/known_faces/person_name/*.jpg")
        return False
    
    print(f"✅ Found {len(image_counts)} persons with {total_images} total images:")
    for person, count in image_counts.items():
        print(f"   - {person}: {count} images")
    
    if total_images < 10:
        print("⚠️  WARNING: Very few training images. Recommend at least 10 per person.")
    
    print()
    
    # Initialize the recognition system
    print("🔧 Initializing EfficientNet B7 system...")
    recognizer = ImprovedEfficientNetFaceRecognitionSystem()
    print("✅ System initialized")
    print()
    
    # Train the model
    print("🎓 Starting training process...")
    print("   This may take 10-15 minutes depending on your hardware")
    print("   The model will learn features from scratch (no ImageNet weights)")
    print()
    
    try:
        # Train with the known faces directory
        success = recognizer.train_with_authorized_faces(str(known_faces_dir))
        
        if success:
            print()
            print("=" * 80)
            print("✅ TRAINING COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            
            # Save the model
            output_path = str(ai_models_path / "improved_efficientnet_face_model")
            print(f"💾 Saving model to: {output_path}")
            
            save_success = recognizer.save_model(output_path)
            
            if save_success:
                print("✅ Model saved successfully!")
                print()
                print("📊 Model Information:")
                print(f"   - Authorized persons: {', '.join(recognizer.authorized_persons)}")
                print(f"   - Model files created:")
                print(f"     • {output_path}_classifier.h5")
                print(f"     • {output_path}_data.pkl")
                print()
                print("🎯 Next Steps:")
                print("   1. Test the model: python test_mediapipe_recognition.py")
                print("   2. Start surveillance: python multi_camera_surveillance.py")
                print()
                print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print("❌ ERROR: Failed to save model")
                return False
        else:
            print()
            print("❌ ERROR: Training failed")
            print("   Check the error messages above for details")
            return False
            
    except KeyboardInterrupt:
        print()
        print("⚠️  Training interrupted by user")
        return False
    except Exception as e:
        print()
        print(f"❌ ERROR: Training failed with exception:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
