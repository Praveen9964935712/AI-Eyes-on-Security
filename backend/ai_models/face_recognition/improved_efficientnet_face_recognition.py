import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB7
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization, Input
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import mediapipe as mp
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import pickle
from datetime import datetime
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

class ImprovedEfficientNetFaceRecognitionSystem:
    def __init__(self):
        """Initialize the Improved EfficientNet B7 Face Recognition System."""
        print("Loading EfficientNet B7 model...")
        
        # Load EfficientNet B7 (frozen for feature extraction)
        # Use weights=None to match your training configuration
        self.base_model = EfficientNetB7(
            weights=None,  # Your model was trained without ImageNet weights
            include_top=False,
            input_shape=(224, 224, 3),
            pooling='avg'  # Add global average pooling
        )
        self.base_model.trainable = False  # Freeze base model
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.7
        )
        
        # Initialize variables
        self.classifier_model = None
        self.label_encoder = None
        self.authorized_persons = []
        self.known_face_encodings = []
        self.known_face_names = []
        
        print("EfficientNet B7 model loaded successfully!")
    
    def _build_improved_classifier(self, num_classes: int, input_dim: int = 2560):
        """Build an improved classifier with better architecture."""
        # Create a separate classifier model that takes pre-extracted features
        # Input layer for pre-extracted features
        inputs = Input(shape=(input_dim,))
        x = BatchNormalization()(inputs)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = BatchNormalization()(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)
        predictions = Dense(num_classes, activation='softmax')(x)
        
        # Create the classifier model
        self.classifier_model = Model(inputs=inputs, outputs=predictions)
        
        # Compile with appropriate settings
        self.classifier_model.compile(
            optimizer=Adam(learning_rate=0.0001),  # Lower learning rate
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("Improved classifier model built successfully!")
    
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
            
            # Extract features using the base model (pooling already built-in)
            features = self.base_model.predict(face_preprocessed, verbose=0)
            
            return features[0]  # Return flattened features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def detect_faces(self, image):
        """Detect faces using MediaPipe Face Detection."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        face_locations = []
        if results.detections:
            h, w, _ = image.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Add padding and ensure bounds
                padding = 20
                top = max(0, y - padding)
                left = max(0, x - padding) 
                bottom = min(h, y + height + padding)
                right = min(w, x + width + padding)
                
                face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def create_augmented_data(self, image, num_augmentations=3):
        """Create augmented versions of training images."""
        augmented_images = [image]
        
        # Data augmentation techniques
        datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            brightness_range=[0.8, 1.2],
            zoom_range=0.1,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Generate augmented images
        image_array = np.expand_dims(image, axis=0)
        i = 0
        for batch in datagen.flow(image_array, batch_size=1):
            if i >= num_augmentations:
                break
            augmented_images.append(batch[0].astype(np.uint8))
            i += 1
        
        return augmented_images
    
    def train_with_authorized_faces(self, authorized_faces_path: str = "authorized_faces"):
        """Train the model with improved data processing and augmentation."""
        print("\n=== Training Mode ===")
        print("Loading and processing authorized faces with improved EfficientNet B7...")
        
        all_features = []
        all_labels = []
        person_names = []
        
        # Process each authorized person
        for person_folder in sorted(os.listdir(authorized_faces_path)):
            person_path = os.path.join(authorized_faces_path, person_folder)
            if not os.path.isdir(person_path):
                continue
                
            print(f"Processing faces for: {person_folder}")
            person_names.append(person_folder)
            person_features = []
            
            for image_file in sorted(os.listdir(person_path)):
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(person_path, image_file)
                    
                    # Load and process image
                    image = cv2.imread(image_path)
                    if image is None:
                        continue
                    
                    # Detect face
                    face_locations = self.detect_faces(image)
                    if not face_locations:
                        print(f"  - No face detected in {image_file}")
                        continue
                    
                    # Extract face
                    top, right, bottom, left = face_locations[0]
                    face_image = image[top:bottom, left:right]
                    
                    if face_image.size == 0 or face_image.shape[0] < 50 or face_image.shape[1] < 50:
                        continue
                    
                    # Create augmented versions for training diversity
                    augmented_faces = self.create_augmented_data(face_image, num_augmentations=2)
                    
                    for aug_face in augmented_faces:
                        features = self.extract_face_features(aug_face)
                        if features is not None:
                            person_features.append(features)
                            all_labels.append(person_folder)
                    
                    print(f"  - Processed {image_file} with {len(augmented_faces)} variations")
            
            all_features.extend(person_features)
            print(f"  - Total features for {person_folder}: {len(person_features)}")
        
        if len(all_features) == 0:
            print("No valid face features extracted!")
            return
        
        # Prepare data
        X = np.array(all_features)
        y = np.array(all_labels)
        
        print(f"\nDataset summary:")
        for person in person_names:
            count = sum(1 for label in y if label == person)
            print(f"  {person}: {count} samples")
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Convert to categorical
        num_classes = len(np.unique(y_encoded))
        y_categorical = tf.keras.utils.to_categorical(y_encoded, num_classes)
        
        # Build improved classifier with correct input dimension
        input_dim = X.shape[1] if len(X) > 0 else 2560
        self._build_improved_classifier(num_classes, input_dim)
        
        # Calculate class weights for balanced training
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_encoded),
            y=y_encoded
        )
        class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_categorical, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        print(f"\nTraining classifier with {len(X_train)} training samples and {len(X_val)} validation samples...")
        
        # Callbacks for better training
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True, monitor='val_accuracy'),
            ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-7, monitor='val_accuracy')
        ]
        
        # Train the model
        history = self.classifier_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=16,
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        train_loss, train_acc = self.classifier_model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_acc = self.classifier_model.evaluate(X_val, y_val, verbose=0)
        
        print(f"\nTraining completed!")
        print(f"Training accuracy: {train_acc:.4f}")
        print(f"Validation accuracy: {val_acc:.4f}")
        
        # Store authorized persons
        self.authorized_persons = person_names
        print(f"Authorized persons: {', '.join(self.authorized_persons)}")
        
        # Save the model
        self.save_model("improved_efficientnet_face_model")
        print("\nTraining completed and model saved!")
    
    def save_model(self, model_path: str):
        """Save the trained classifier model and encoders."""
        data = {
            'authorized_persons': self.authorized_persons,
            'label_encoder': self.label_encoder
        }
        
        # Save classifier model
        if self.classifier_model:
            self.classifier_model.save(f"{model_path}_classifier.h5")
            print(f"Classifier model saved to {model_path}_classifier.h5")
        
        # Save other data
        with open(f"{model_path}_data.pkl", 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Model data saved to {model_path}_data.pkl")
    
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
        Recognize faces in a video frame using improved EfficientNet B7.
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
                
                # More reasonable confidence threshold
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
    
    def start_live_recognition(self, camera_index: int = 0):
        """Start live face recognition from camera."""
        print("Starting improved EfficientNet B7 live face recognition...")
        print("Press 'q' to quit")
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Starting camera...")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Process every 3rd frame for performance
            if frame_count % 3 == 0:
                # Recognize faces
                face_names, face_locations, verification_results = self.recognize_faces_in_frame(frame)
                
                # Log results with timestamp
                if face_names:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for name, result in zip(face_names, verification_results):
                        if result == 1:
                            print(f"[{timestamp}] {name}: {result}")
                
                # Draw rectangles and labels
                for (name, (top, right, bottom, left), result) in zip(face_names, face_locations, verification_results):
                    # Choose color based on verification result
                    color = (0, 255, 0) if result == 1 else (0, 0, 255)  # Green for authorized, red for unauthorized
                    
                    # Draw rectangle around face
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    
                    # Draw label
                    label = f"{name}" if result == 1 else "Unauthorized"
                    cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('Improved EfficientNet B7 Face Recognition', frame)
            
            frame_count += 1
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

def main():
    """Main function to run the improved face recognition system."""
    system = ImprovedEfficientNetFaceRecognitionSystem()
    
    while True:
        print("\n=== Improved EfficientNet B7 Face Recognition Security System ===")
        print("1. Train with authorized faces")
        print("2. Start live recognition")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            system.train_with_authorized_faces()
        elif choice == '2':
            if system.load_model():
                system.start_live_recognition()
            else:
                print("No trained model found. Please train the system first (option 1)")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()