#!/usr/bin/env python3
"""
Simple Live IP Camera Surveillance
Real-time processing of your IP camera with AI detection and alerts
"""

import sys
import os
import cv2
import time
from datetime import datetime

sys.path.append('.')
from surveillance.detector import YOLOv9Detector

def run_live_surveillance():
    """Run live surveillance on your IP camera"""
    
    # Your camera URL
    camera_url = "http://192.168.137.254:8080/video"
    
    print("=" * 60)
    print("🔍 LIVE AI SURVEILLANCE SYSTEM")
    print("=" * 60)
    print(f"📹 Camera: {camera_url}")
    print("🤖 AI: YOLOv9 + Activity Analysis")
    print("⚠️  Press 'q' to quit, 's' to save screenshot")
    print("=" * 60)
    
    # Initialize detector
    detector = YOLOv9Detector(conf_threshold=0.3)  # Lower threshold to see more detections
    
    # Connect to camera
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("❌ ERROR: Cannot connect to camera!")
        return
    
    # Tracking variables
    frame_count = 0
    last_alert_time = 0
    total_detections = 0
    alert_count = 0
    person_history = []
    
    print("🟢 SURVEILLANCE ACTIVE - Processing live feed...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Cannot read frame, retrying...")
                time.sleep(1)
                continue
            
            frame_count += 1
            current_time = time.time()
            
            # AI Detection
            detections = detector.detect(frame)
            persons = detector.filter_persons(detections)
            weapons = detector.filter_weapons(detections)
            bags = detector.filter_bags(detections)
            
            total_detections += len(detections)
            
            # Create display frame
            display_frame = frame.copy()
            
            # Draw detections
            for detection in detections:
                bbox = detection['bbox']
                class_name = detection['class_name']
                confidence = detection['confidence']
                
                # Color coding
                if class_name == 'person':
                    color = (0, 255, 0)  # Green
                elif detection['class_id'] in [34, 43, 76]:  # Weapons
                    color = (0, 0, 255)  # Red
                elif class_name in ['backpack', 'handbag', 'suitcase']:
                    color = (255, 165, 0)  # Orange
                else:
                    color = (255, 255, 0)  # Yellow
                
                # Draw bounding box
                cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                # Draw label
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(display_frame, label, (bbox[0], bbox[1]-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Activity Analysis
            person_count = len(persons)
            person_history.append(person_count)
            if len(person_history) > 30:  # Keep last 30 frames (1 second at 30fps)
                person_history.pop(0)
            
            alerts = []
            
            # Check for suspicious activities
            if weapons:
                alerts.append(f"🚨 WEAPON DETECTED: {weapons[0]['class_name']}")
                alert_count += 1
            
            if person_count > 3:
                alerts.append(f"👥 CROWD ALERT: {person_count} persons detected")
            
            if person_count == 0 and len(bags) > 0:
                alerts.append(f"👜 ABANDONED BAG: Unattended object detected")
            
            # Check for loitering (person count stable for extended period)
            if len(person_history) >= 30 and person_count > 0:
                avg_persons = sum(person_history) / len(person_history)
                if abs(avg_persons - person_count) < 0.5:  # Stable person count
                    alerts.append(f"⏰ LOITERING: {person_count} person(s) stationary")
            
            # Display alerts on frame
            y_offset = 30
            for alert in alerts:
                cv2.putText(display_frame, alert, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_offset += 30
                
                # Print alerts to console (with cooldown)
                if current_time - last_alert_time > 5:  # Alert every 5 seconds max
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {alert}")
                    last_alert_time = current_time
            
            # Add status overlay
            status_text = f"Frame: {frame_count} | Objects: {len(detections)} | Persons: {person_count} | Alerts: {alert_count}"
            cv2.putText(display_frame, status_text, (10, display_frame.shape[0]-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(display_frame, timestamp, (10, display_frame.shape[0]-40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow('🔍 Live AI Surveillance', display_frame)
            
            # Console output every 30 frames
            if frame_count % 30 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {frame_count} frames | "
                      f"Total detections: {total_detections} | Current: {len(detections)} objects, {person_count} persons")
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save screenshot
                filename = f"surveillance_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Screenshot saved: {filename}")
            
            # Small delay for stability
            time.sleep(0.03)  # ~30 FPS
    
    except KeyboardInterrupt:
        print("\n🛑 Surveillance stopped by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("📊 SURVEILLANCE SESSION SUMMARY")
        print("=" * 60)
        print(f"📹 Total frames processed: {frame_count}")
        print(f"🎯 Total detections: {total_detections}")
        print(f"⚠️ Alert events: {alert_count}")
        print(f"⏱️ Session duration: {frame_count/30:.1f} seconds")
        print("=" * 60)

if __name__ == "__main__":
    run_live_surveillance()