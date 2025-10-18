import sys; sys.path.insert(0, 'ai_models/face_recognition')
from improved_efficientnet_face_recognition import ImprovedEfficientNetFaceRecognitionSystem
import cv2
import numpy as np

r = ImprovedEfficientNetFaceRecognitionSystem()
r.load_model('ai_models/face_recognition/improved_efficientnet_face_model')

frame = cv2.imread('data/known_faces/manager_prajwal/manager_prajwal_1.jpg')
locs = r.detect_faces(frame)
face = frame[locs[0][0]:locs[0][2], locs[0][3]:locs[0][1]]
feat = r.extract_face_features(face)
pred = r.classifier_model.predict(feat.reshape(1,-1), verbose=0)

print('Predictions:')
for i, p in enumerate(pred[0]):
    print(f'{r.label_encoder.inverse_transform([i])[0]}: {p:.3f}')
