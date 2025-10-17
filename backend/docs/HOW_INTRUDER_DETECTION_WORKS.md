# 🚨 HOW INTRUDER DETECTION & ALERTING WORKS

## 📊 **COMPLETE FLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMERA FEED (Every Frame)                    │
│           http://192.168.137.254:8080/video                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: YOLOv9 OBJECT DETECTION                     │
│  Detects: person, car, laptop, cell phone, etc.                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴──────────┐
                    │  Person Detected?  │
                    └─────────┬──────────┘
                              │
                   ┌──────────┴──────────┐
                   NO                   YES
                   │                     │
                   ↓                     ↓
        ┌──────────────────┐  ┌─────────────────────────┐
        │ Skip Face Check  │  │ STEP 2: FACE DETECTION  │
        │ (No alerts)      │  │ (OpenCV Haar Cascade)   │
        └──────────────────┘  └─────────────────────────┘
                                         ↓
                              ┌──────────┴──────────┐
                              │ Faces Detected?     │
                              └──────────┬──────────┘
                                         │
                          ┌──────────────┼──────────────┐
                          │              │              │
                       0 FACES        1+ FACES      FACE TOO SMALL
                          │              │              │
                          ↓              ↓              ↓
              ┌─────────────────┐  ┌────────────────────────┐
              │ Person but no   │  │ STEP 3: FACE           │
              │ face visible    │  │ RECOGNITION (LBPH)     │
              │ → INTRUDER      │  │                        │
              │ (Face hidden)   │  │ Compare with trained:  │
              └─────────────────┘  │ - farmer_Basava        │
                                   │ - manager_prajwal      │
                                   │ - owner_rajasekhar     │
                                   └────────────────────────┘
                                              ↓
                                   ┌──────────────────────┐
                                   │ Calculate Confidence │
                                   │ (Lower = Better)     │
                                   └──────────────────────┘
                                              ↓
                          ┌───────────────────┴───────────────────┐
                          │                                       │
                   Confidence ≤ 60                        Confidence > 60
                   (GOOD MATCH)                          (POOR MATCH)
                          │                                       │
                          ↓                                       ↓
              ┌────────────────────────┐              ┌─────────────────────┐
              │  ✅ AUTHORIZED         │              │  ❌ INTRUDER        │
              │                        │              │                     │
              │  farmer_Basava (56)    │              │  unknown (85)       │
              │  manager_prajwal (57)  │              │  stranger (72)      │
              │  owner_rajasekhar (58) │              │  random person (68) │
              └────────────────────────┘              └─────────────────────┘
                          │                                       │
                          ↓                                       ↓
              ┌────────────────────────┐              ┌─────────────────────┐
              │  NO ALERT SENT         │              │  🚨 ALERT SENT!     │
              │  ℹ️ Console shows:     │              │                     │
              │  "AUTHORIZED: ...      │              │  1. Save snapshot   │
              │   Access granted"      │              │  2. Email alert     │
              │  "No alerts"           │              │  3. Console warn    │
              └────────────────────────┘              │  4. Log to memory   │
                                                      └─────────────────────┘
```

---

## 🎯 **CONFIDENCE THRESHOLD SYSTEM**

### **How It Works:**

The system compares each detected face with ALL 3 authorized personnel:
- farmer_Basava (36 training images)
- manager_prajwal (21 training images)  
- owner_rajasekhar (30 training images)

**Lower confidence score = Better match** (counter-intuitive!)

### **Threshold: 60 (BALANCED)**

```
┌──────────────────────────────────────────────────────────────────┐
│  CONFIDENCE SCALE (Lower = Better)                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  0-40   ████████████████  PERFECT MATCH (Same person)            │
│         └─ Example: farmer_Basava shows face → 35-45            │
│                                                                   │
│  40-60  ████████████      GOOD MATCH → ✅ AUTHORIZED             │
│         ├─ Threshold Line: 60                                    │
│         └─ Your authorized people: 56-58                         │
│                                ↑                                 │
│                          THRESHOLD = 60                          │
│                                ↓                                 │
│  60-80  ████████          POOR MATCH → ❌ INTRUDER               │
│         └─ Strangers/You: 65-85                                  │
│                                                                   │
│  80-100 ████              VERY POOR MATCH → ❌ INTRUDER          │
│         └─ Random people: 90-95                                  │
│                                                                   │
│  100+   ██                COMPLETELY DIFFERENT → ❌ INTRUDER      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### **Decision Logic:**

```python
if confidence <= 60:
    status = "AUTHORIZED"
    send_alert = False
    console_message = "✅ AUTHORIZED: {name} - Access granted"
else:
    status = "INTRUDER"
    send_alert = True
    console_message = "🚨 INTRUDER DETECTED"
```

---

## 🚨 **WHAT TRIGGERS AN INTRUDER ALERT?**

### **Scenario A: Unknown Face (Stranger)**

```
Camera detects: 1 person
Face detection: 1 face found
Face recognition: Compares with all 3 authorized persons
Best match: owner_rajasekhar (confidence: 85)
Decision: 85 > 60 → INTRUDER! 🚨

Actions:
  1. ✅ Save snapshot: storage/snapshots/intruder_Camera_1_Manual_20251017_104735.jpg
  2. ✅ Send email alert (if not in cooldown)
  3. ✅ Console warning: "🚨 INTRUDER DETECTED: 1 unauthorized person(s)"
  4. ✅ Log to alert history
```

### **Scenario B: Authorized Person (farmer_Basava)**

```
Camera detects: 1 person
Face detection: 1 face found
Face recognition: Compares with all 3 authorized persons
Best match: farmer_Basava (confidence: 56)
Decision: 56 < 60 → AUTHORIZED! ✅

Actions:
  1. ❌ NO snapshot saved
  2. ❌ NO email sent
  3. ✅ Console message: "✅ AUTHORIZED: farmer_Basava - Access granted"
  4. ✅ Console message: "ℹ️ INFO: Only authorized personnel - no alerts"
```

### **Scenario C: Person with Hidden Face**

```
Camera detects: 1 person
Face detection: 0 faces found (face turned away/covered)
Decision: Person with no visible face = SUSPICIOUS! 🚨

Actions:
  1. ✅ Save snapshot
  2. ✅ Send email alert
  3. ✅ Console: "🚨 INTRUDER: Person detected but face not visible - potential intruder"
  4. ✅ Treat as intruder (security measure)
```

### **Scenario D: Multiple People (Mixed)**

```
Camera detects: 3 persons
Face detection: 3 faces found
Face recognition:
  - Face 1: farmer_Basava (confidence: 56) → AUTHORIZED ✅
  - Face 2: unknown (confidence: 78) → INTRUDER ❌
  - Face 3: owner_rajasekhar (confidence: 58) → AUTHORIZED ✅

Decision: INTRUDERS PRESENT! 🚨 (Even though authorized also present)

Actions:
  1. ✅ Save snapshot with ALL faces
  2. ✅ Send email alert
  3. ✅ Console: "🚨 INTRUDER DETECTED: 1 unauthorized person(s)"
  4. ✅ Console: "⚠️ SECURITY WARNING: Intruder alongside authorized personnel"
  5. ✅ Email mentions both: "INTRUDER with farmer_Basava, owner_rajasekhar also present"
```

---

## 📧 **EMAIL ALERT SYSTEM**

### **When Email is Sent:**

✅ **ALWAYS** when:
- Intruder detected (confidence > 60)
- Person with hidden face detected
- Weapon detected (critical alert)

❌ **NEVER** when:
- Only authorized personnel present (confidence ≤ 60)
- No persons detected
- Alert in cooldown period (5 minutes)

### **Email Cooldown:**

```
First intruder detected → Email sent immediately ✅
Same intruder 2 minutes later → Email blocked (cooldown) ❌
Same intruder 6 minutes later → Email sent again ✅

Cooldown prevents spam: 5 minutes between emails of same type
```

### **Email Content:**

**Subject:** `🚨 CRITICAL ALERT: Intruder Detected - AI Eyes Security`

**Body (HTML):**
```
🚨 SECURITY ALERT

Type: Intruder Detection
Location: Camera Camera_1_Manual
Time: 2025-10-17 10:47:35

Description:
Unauthorized person detected in farm area: unknown

Severity: HIGH
Confidence: N/A

Action Required:
Please verify and respond to this security incident.

[SNAPSHOT IMAGE ATTACHED]

---
AI Eyes Security System
Automated Farm Surveillance
```

**Attachment:**
- Snapshot image showing the intruder
- Filename: `intruder_Camera_1_Manual_20251017_104735.jpg`

---

## 🎯 **YOUR CURRENT SCENARIO**

### **Problem Before Fix:**
```
You show face to camera
System compares with 3 authorized persons
Best match: manager_prajwal (confidence: 66)
Threshold was: 55
Decision: 66 > 55 → Authorized people REJECTED as intruders! ❌

farmer_Basava shows face
Best match: farmer_Basava (confidence: 56)
Threshold was: 55
Decision: 56 > 55 → REJECTED AS INTRUDER! ❌ WRONG!
```

### **Solution (Threshold 60):**
```
You show face to camera
Best match: manager_prajwal (confidence: 66)
Threshold now: 60
Decision: 66 > 60 → INTRUDER ✅ CORRECT!
Email sent: "Unauthorized person detected"

farmer_Basava shows face
Best match: farmer_Basava (confidence: 56)
Threshold now: 60
Decision: 56 < 60 → AUTHORIZED ✅ CORRECT!
No email sent: "Only authorized personnel - no alerts"
```

---

## 🔍 **FACE DETECTION PARAMETERS**

### **Why Strict Parameters?**

**Before (Too Sensitive):**
```
scaleFactor: 1.1   → Very sensitive, detects posters/photos
minNeighbors: 5    → Low confidence threshold
minSize: (15, 15)  → Detects tiny patterns as faces

Result: 9 faces detected from 1 person! ❌
```

**After (Balanced):**
```
scaleFactor: 1.3   → Less sensitive, ignores photos/patterns
minNeighbors: 8    → Higher confidence required
minSize: (60, 60)  → Only real face sizes detected

Result: 1-2 faces detected (real faces only) ✅
```

### **What Gets Filtered Out:**

❌ **Ignored (Too Small/Uncertain):**
- Posters on wall (small faces)
- Photos in background
- Patterns/logos that look like faces
- Reflections in mirrors/screens
- Face-like shadows

✅ **Detected (Real Faces):**
- Actual person standing in front of camera
- Clear, visible face (60x60 pixels minimum)
- Face with good lighting
- Front or 45° angle faces

---

## 📊 **COMPLETE ALERT FLOW**

```
┌──────────────────────────────────────────────────────────────┐
│  1. DETECTION PHASE                                          │
│     YOLOv9 → Person detected? YES                            │
│     OpenCV → Face found? YES (1 face, 60x80 pixels)          │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  2. RECOGNITION PHASE                                        │
│     LBPH Face Recognizer compares with 3 authorized persons: │
│       - farmer_Basava: confidence 85 (poor match)            │
│       - manager_prajwal: confidence 72 (poor match)          │
│       - owner_rajasekhar: confidence 78 (poor match)         │
│     Best match: manager_prajwal at 72                        │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  3. DECISION PHASE                                           │
│     Confidence: 72                                           │
│     Threshold: 60                                            │
│     Decision: 72 > 60 → INTRUDER! 🚨                         │
│     Person name: "unknown"                                   │
│     Status: "intruder"                                       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  4. SNAPSHOT PHASE                                           │
│     Timestamp: 2025-10-17 10:47:35                           │
│     Filename: intruder_Camera_1_Manual_20251017_104735.jpg   │
│     Location: storage/snapshots/                             │
│     Action: cv2.imwrite(snapshot_path, frame) ✅             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  5. ALERT MANAGER PHASE                                      │
│     Alert type: "intruder"                                   │
│     Severity: "high"                                         │
│     Camera: "Camera_1_Manual"                                │
│     Image path: snapshot_path                                │
│     Method: alert_manager.send_intruder_alert(...)           │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  6. EMAIL COOLDOWN CHECK                                     │
│     Last intruder email: 5 minutes ago                       │
│     Current time: Now                                        │
│     Cooldown period: 5 minutes                               │
│     Decision: 5 min >= 5 min → ✅ SEND EMAIL                 │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  7. EMAIL SENDING PHASE (SendGrid)                           │
│     Service: SendGrid API                                    │
│     From: praveenkumarnaik14@gmail.com                       │
│     To: praveenkumarnaik14@gmail.com                         │
│     Subject: "🚨 CRITICAL ALERT: Intruder Detected"          │
│     Body: HTML template with snapshot attachment             │
│     Status: ✅ Email sent successfully                       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  8. CONSOLE OUTPUT PHASE                                     │
│     Print messages:                                          │
│     🟠 Alert [HIGH]: intruder at Camera_1_Manual (Email: ✅) │
│     🚨 ALERT: INTRUDER DETECTED: 1 unauthorized person(s)    │
│     📸 Snapshot saved: storage\snapshots\intruder_...        │
│     🚨 INTRUDERS ONLY: No authorized personnel detected      │
│     ✅ Alert email sent successfully for intruder            │
│     📧 Email alert sent successfully for intruder            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  9. MEMORY STORAGE PHASE                                     │
│     Store in alert_history (last 100 alerts)                 │
│     Store in active_alerts dictionary                        │
│     Update statistics:                                       │
│       - total_alerts++                                       │
│       - emails_sent++                                        │
│       - last_alert_time = now                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 **TESTING GUIDE**

### **Test 1: Show Authorized Person (Should NOT Alert)**

**Person:** farmer_Basava, manager_prajwal, or owner_rajasekhar

**Expected Console Output:**
```
0: 384x640 1 person, 440ms
👤 Face Detection for Camera_1_Manual: 1 faces detected
👤 Face Recognition Results for Camera_1_Manual:
   Face 1: farmer_Basava (confidence: 56.00, status: authorized)

✅ AUTHORIZED [Camera_Camera_1_Manual]: farmer_Basava - Access granted
ℹ️ INFO: Only authorized personnel detected - no alerts
```

**Expected Result:**
- ✅ Face recognized correctly
- ❌ NO snapshot saved
- ❌ NO email sent
- ✅ Console shows "AUTHORIZED"

---

### **Test 2: Show Unauthorized Person (Should Alert)**

**Person:** You, or any stranger

**Expected Console Output:**
```
0: 384x640 1 person, 440ms
👤 Face Detection for Camera_1_Manual: 1 faces detected
👤 Face Recognition Results for Camera_1_Manual:
   Face 1: unknown (confidence: 72.00, status: intruder)

🟠 Alert [HIGH]: intruder at Camera Camera_1_Manual (Email: ✅)
🚨 ALERT [Camera_Camera_1_Manual]: INTRUDER DETECTED: 1 unauthorized person(s)
📸 Snapshot saved: storage\snapshots\intruder_Camera_1_Manual_20251017_HHMMSS.jpg
🚨 INTRUDERS ONLY: No authorized personnel detected - intruder alert sent
✅ Alert email sent successfully for intruder
📧 Email alert sent successfully for intruder
```

**Expected Result:**
- ✅ Face detected but not recognized
- ✅ Snapshot saved
- ✅ Email sent (if not in cooldown)
- ✅ Console shows "INTRUDER DETECTED"

---

### **Test 3: Person Hiding Face (Should Alert)**

**Person:** Anyone, but turn face away from camera

**Expected Console Output:**
```
0: 384x640 1 person, 440ms
👤 Face Detection for Camera_1_Manual: 0 faces detected
🚨 INTRUDER: Person detected but face not visible - potential intruder
🟠 Alert [HIGH]: intruder at Camera Camera_1_Manual (Email: ✅)
```

**Expected Result:**
- ✅ Person detected by YOLOv9
- ❌ No face detected
- ✅ Treated as suspicious intruder
- ✅ Snapshot + email sent

---

## ⚙️ **CONFIGURATION FILES**

### **Where Threshold is Set:**

**File:** `backend/multi_camera_surveillance.py`
**Line:** ~71

```python
self.face_recognizer = LBPHFaceRecognizer(
    known_faces_dir="data/known_faces",
    confidence_threshold=60.0  # ← CHANGE THIS VALUE
)
```

**Adjustment Guide:**
- **50:** Very strict (may reject real authorized people)
- **55:** Strict (rejected your people at 56-58) ❌
- **60:** **BALANCED** (accepts 56-58, rejects 65+) ✅ CURRENT
- **70:** Lenient (accepted strangers at 66) ❌
- **80:** Very lenient (security risk)

---

### **Where Face Detection Parameters are Set:**

**File:** `backend/surveillance/face_recognition.py`
**Line:** ~82

```python
faces = self.face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.3,    # ← Sensitivity (1.1-1.5)
    minNeighbors=8,     # ← Evidence required (5-10)
    minSize=(60, 60),   # ← Minimum face size
    maxSize=(400, 400)
)
```

---

## 📈 **STATISTICS & MONITORING**

### **Alert Statistics (In Memory):**

```python
{
    'total_alerts': 127,
    'emails_sent': 15,
    'email_failures': 0,
    'alerts_by_type': {
        'intruder': 102,
        'weapon': 0,
        'suspicious_activity': 25
    },
    'recent_alerts': [last 10 alerts]
}
```

### **Check Alert History:**

**API Endpoint:** `http://localhost:5002/api/alerts`

**Response:**
```json
[
  {
    "id": "ALERT_1729154855000",
    "type": "intruder",
    "severity": "high",
    "description": "INTRUDER DETECTED: 1 unauthorized person(s)",
    "camera_id": "Camera_1_Manual",
    "timestamp": "2025-10-17T10:47:35",
    "image_path": "storage/snapshots/intruder_Camera_1_Manual_20251017_104735.jpg"
  }
]
```

---

## 🔧 **TROUBLESHOOTING**

### **Issue: Authorized person detected as intruder**

**Symptoms:**
```
Face 1: farmer_Basava (confidence: 56, status: intruder)  ❌
```

**Cause:** Threshold too strict (below 56)

**Solution:** Increase threshold to 60
```python
confidence_threshold=60.0  # Was 55, now 60
```

---

### **Issue: Stranger detected as authorized**

**Symptoms:**
```
Face 1: unknown (confidence: 68, status: authorized)  ❌
```

**Cause:** Threshold too lenient (above 68)

**Solution:** Decrease threshold to 60
```python
confidence_threshold=60.0  # Was 70, now 60
```

---

### **Issue: Too many faces detected (9 faces from 1 person)**

**Cause:** Face detection too sensitive

**Solution:** Already applied! Stricter parameters:
```python
scaleFactor=1.3,    # Less sensitive
minNeighbors=8,     # More evidence
minSize=(60, 60)    # Larger minimum
```

---

### **Issue: Email not sent**

**Check:**
1. Email service enabled? 
   ```
   📧 Email service status: {'enabled': True}
   ```
2. Alert in cooldown?
   ```
   🟠 Alert [HIGH]: intruder (Email: ❌ Cooldown)
   ```
3. SendGrid API key set?
   ```
   'api_key_set': True
   ```

**If cooldown, wait 5 minutes or check:**
```
Last email: 10:47:35
Current time: 10:49:00
Time difference: 1 min 25 sec < 5 min cooldown
Result: Email blocked ❌
```

---

## ✅ **SUMMARY: How It Works**

1. **Camera captures frame** → Every frame analyzed
2. **YOLOv9 detects person** → If person found, proceed to face detection
3. **OpenCV finds faces** → Using strict parameters (60px minimum, 8 neighbors)
4. **LBPH recognizes face** → Compare with 3 authorized persons
5. **Confidence checked** → If ≤ 60: authorized, if > 60: intruder
6. **Intruder triggers alert** → Save snapshot, send email, log to console
7. **Email sent via SendGrid** → With snapshot attachment (if not in cooldown)
8. **Console displays result** → Real-time feedback for monitoring

**Key Decision Point:**
```python
if confidence <= 60:
    # Authorized person
    print("✅ AUTHORIZED")
    # NO alert, NO email, NO snapshot
else:
    # Intruder detected
    print("🚨 INTRUDER")
    # Save snapshot, send email, create alert
```

---

**Date:** October 17, 2025  
**System Status:** ✅ Operational  
**Threshold:** 60 (BALANCED mode)  
**Email Service:** SendGrid (Enabled)  
**Alert Cooldown:** 5 minutes
