"""
EfficientNet Face Recognition System - Modified for OpenCV Face Detection
Works without MediaPipe - uses OpenCV Haar Cascade instead
Compatible with Python 3.13
"""

import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB7
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

class ImprovedEfficientNetFaceRecognitionSystem:
    def __init__(self):
        """Initialize the Improved EfficientNet B7 Face Recognition System with OpenCV."""
        print("Loading EfficientNet B7 model...")
        
        # Initialize OpenCV Face Detection first (Haar Cascade)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            raise Exception("Error loading face cascade classifier")
        
        print("Using OpenCV Haar Cascade for face detection")
        
        # Load EfficientNet B7 (frozen for feature extraction)
        # Use weights=None to match training (your model was trained without ImageNet weights)
        print("Loading EfficientNet B7 base model...")
        self.base_model = EfficientNetB7(
            weights=None,  # Match your training setup
            include_top=False,
            input_shape=(224, 224, 3),
            pooling='avg'  # Add global average pooling
        )
        self.base_model.trainable = False  # Freeze base model
        print("✅ EfficientNet B7 base model loaded (matching your training configuration)")
        
        # Initialize variables
        self.classifier_model = None
        self.label_encoder = None
        self.authorized_persons = []
        
        print("EfficientNet B7 model loaded successfully with OpenCV face detection!")
    
    def extract_face_features(self, face_image):
        """Extract features from a face image using EfficientNet B7."""
        try:
            # Enhanced preprocessing
            if face_image.shape[0] < 50 or face_image.shape[1] < 50:
                return None
            
            # Resize with better interpolation
            face_resized = cv2.resize(face_image, (224, 224), interpolation=cv2.INTER_LANCZOS4)
            
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values
            face_rgb = face_rgb.astype(np.float32) / 255.0
            
            # Expand dimensions and apply EfficientNet preprocessing
            face_array = np.expand_dims(face_rgb, axis=0)
            face_preprocessed = preprocess_input(face_array * 255.0)
            
            # Extract features using the base model (with built-in pooling)
            features = self.base_model.predict(face_preprocessed, verbose=0)
            
            # Features are already pooled, just flatten
            return features[0]  # Return flattened features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def detect_faces(self, image):
        """Detect faces using OpenCV Haar Cascade."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with optimized parameters
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        face_locations = []
        h, w, _ = image.shape
        
        for (x, y, width, height) in faces:
            # Add padding
            padding = 20
            top = max(0, y - padding)
            left = max(0, x - padding)
            bottom = min(h, y + height + padding)
            right = min(w, x + width + padding)
            
            face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def load_model(self, model_path: str = "improved_efficientnet_face_model") -> bool:
        """Load the trained classifier model and encoders."""
        try:
            # Load classifier model
            classifier_path = f"{model_path}_classifier.h5"
            if os.path.exists(classifier_path):
                self.classifier_model = load_model(classifier_path)
                print(f"Classifier model loaded from {classifier_path}")
            else:
                print("No trained classifier model found!")
                return False
            
            # Load other data
            data_path = f"{model_path}_data.pkl"
            if os.path.exists(data_path):
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.authorized_persons = data['authorized_persons']
                self.label_encoder = data['label_encoder']
                
                print("Model data loaded successfully!")
                print(f"Authorized persons: {', '.join(self.authorized_persons)}")
            else:
                print("No model data found!")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def recognize_faces_in_frame(self, frame) -> Tuple[List[str], List[Tuple[int, int, int, int]], List[int]]:
        """
        Recognize faces in a video frame using EfficientNet B7.
        Returns: (names, face_locations, verification_results)
        verification_results: 1 for authorized, 0 for unauthorized
        """
        # Detect faces in the current frame
        face_locations = self.detect_faces(frame)
        
        face_names = []
        verification_results = []
        
        if not face_locations or self.classifier_model is None:
            return face_names, face_locations, verification_results
        
        # Process each detected face
        for (top, right, bottom, left) in face_locations:
            # Extract face region
            face_image = frame[top:bottom, left:right]
            
            if face_image.size == 0:
                face_names.append("Unknown")
                verification_results.append(0)
                continue
            
            # Extract EfficientNet features
            features = self.extract_face_features(face_image)
            
            if features is None:
                face_names.append("Unknown")
                verification_results.append(0)
                continue
            
            # Predict using the trained classifier
            name = "Unknown"
            verification_result = 0
            
            try:
                # Reshape features for prediction
                features_reshaped = features.reshape(1, -1)
                
                # Get prediction probabilities
                predictions = self.classifier_model.predict(features_reshaped, verbose=0)
                
                # Get the most confident prediction
                max_prob_index = np.argmax(predictions[0])
                max_probability = predictions[0][max_prob_index]
                
                # Confidence threshold
                confidence_threshold = 0.50  # 50% confidence required
                
                if max_probability >= confidence_threshold:
                    predicted_label = self.label_encoder.inverse_transform([max_prob_index])[0]
                    name = predicted_label
                    verification_result = 1
                    print(f"Debug: Recognized {name} with confidence {max_probability:.3f}")
                else:
                    print(f"Debug: Rejected - max confidence {max_probability:.3f} < threshold {confidence_threshold}")
                
            except Exception as e:
                print(f"Recognition error: {e}")
            
            face_names.append(name)
            verification_results.append(verification_result)
        
        return face_names, face_locations, verification_results

def main():
    """Test function."""
    system = ImprovedEfficientNetFaceRecognitionSystem()
    
    # Try to load model
    model_path = "improved_efficientnet_face_model"
    if os.path.exists(f"{model_path}_classifier.h5"):
        if system.load_model(model_path):
            print("✅ Model loaded successfully!")
            print(f"✅ Authorized persons: {', '.join(system.authorized_persons)}")
        else:
            print("❌ Failed to load model")
    else:
        print("⚠️ No trained model found. Please train first.")

if __name__ == "__main__":
    main()
