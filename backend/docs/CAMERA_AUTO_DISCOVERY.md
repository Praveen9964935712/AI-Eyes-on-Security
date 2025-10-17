# 📹 Camera Auto-Discovery System

## 🎯 **Overview**

The AI Eyes Security system now **automatically discovers IP cameras** on your network and displays them on the dashboard with **real-time connectivity status** (ONLINE/OFFLINE).

---

## 🚀 **How It Works**

### **1. Auto-Discovery**
The system scans your network to find:
- **IP Webcam** apps (Android/iOS) on ports 8080, 8081, 4747
- **RTSP cameras** on ports 554, 8554
- **HTTP cameras** on ports 80, 8080

### **2. Connectivity Monitoring**
- **Every 30 seconds:** Checks if each camera is reachable
- **Online:** Camera responds to ping/HTTP request
- **Offline:** Camera on different network or powered off

### **3. Database Storage**
Discovered cameras saved to: `backend/storage/database/discovered_cameras.json`

```json
{
  "id": "camera_192_168_137_254_8080",
  "name": "IP Webcam 192.168.137.254",
  "ip": "192.168.137.254",
  "port": 8080,
  "url": "http://192.168.137.254:8080/video",
  "type": "ip_webcam",
  "status": "online",
  "last_seen": "2025-10-17T16:20:00",
  "discovered_at": "2025-10-17T16:00:00"
}
```

---

## 📊 **Dashboard Integration**

### **What You'll See:**

**Active Cameras Card:**
```
Active Cameras: 2
✅ System online
```

**Camera Cards:**
```
┌─────────────────────────────┐
│ 📹 IP Webcam 192.168.137.254│
│ Status: 🟢 ONLINE           │
│ IP: 192.168.137.254:8080    │
│ Type: IP Webcam             │
│ Last Seen: 2 seconds ago    │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 📹 IP Webcam 192.168.1.100  │
│ Status: 🔴 OFFLINE          │
│ IP: 192.168.1.100:8080      │
│ Type: IP Webcam             │
│ Last Seen: 5 minutes ago    │
└─────────────────────────────┘
```

---

## 🔧 **API Endpoints**

### **GET /api/camera/list**
Get all discovered cameras with status

**Response:**
```json
[
  {
    "id": "camera_192_168_137_254_8080",
    "name": "IP Webcam 192.168.137.254",
    "ip": "192.168.137.254",
    "port": 8080,
    "url": "http://192.168.137.254:8080/video",
    "type": "ip_webcam",
    "status": "online",
    "last_seen": "2025-10-17T16:20:00",
    "discovered_at": "2025-10-17T16:00:00",
    "manual": false
  }
]
```

### **POST /api/camera/scan**
Trigger immediate network scan

**Response:**
```json
{
  "message": "Network scan started",
  "status": "scanning"
}
```

### **GET /api/camera/status**
Get discovery service status

**Response:**
```json
{
  "total_cameras": 2,
  "online": 1,
  "offline": 1,
  "scanning": false
}
```

### **POST /api/camera/add**
Manually add camera

**Request:**
```json
{
  "name": "Front Door Camera",
  "url": "http://192.168.1.50:8080/video",
  "type": "ip_webcam"
}
```

**Response:**
```json
{
  "message": "Camera added successfully",
  "camera": { ... }
}
```

### **DELETE /api/camera/remove/{camera_id}**
Remove a camera

**Response:**
```json
{
  "message": "Camera removed successfully"
}
```

---

## 🌐 **Network Detection Logic**

### **Same Network (ONLINE):**
```
Your Computer: 192.168.137.1
IP Webcam:     192.168.137.254
Status:        ✅ ONLINE (same subnet 192.168.137.x)
```

### **Different Network (OFFLINE):**
```
Your Computer: 192.168.137.1
IP Webcam:     192.168.1.100
Status:        ❌ OFFLINE (different subnet 192.168.1.x)
```

### **Powered Off/Unreachable (OFFLINE):**
```
Your Computer: 192.168.137.1
IP Webcam:     192.168.137.254 (powered off)
Status:        ❌ OFFLINE (no response)
```

---

## 🔄 **Automatic Processes**

### **On System Start:**
1. ✅ Load previously discovered cameras from database
2. ✅ Perform initial network scan (takes ~30 seconds)
3. ✅ Start status monitoring (every 30 seconds)
4. ✅ Start background scanning (every 5 minutes)

### **During Operation:**
- **Every 30 seconds:** Update camera online/offline status
- **Every 5 minutes:** Scan network for new cameras
- **On status change:** Update dashboard automatically

---

## 📱 **Supported Camera Types**

### **1. IP Webcam (Android)**
- **App:** IP Webcam by Pavel Khlebovich
- **Default URL:** `http://<phone-ip>:8080/video`
- **Ports:** 8080, 8081, 4747

### **2. RTSP Cameras**
- **Professional security cameras**
- **URL Format:** `rtsp://<camera-ip>:554/stream`
- **Ports:** 554, 8554

### **3. HTTP/MJPEG Cameras**
- **Web-based cameras**
- **URL Format:** `http://<camera-ip>:80/video`
- **Ports:** 80, 8080

---

## 🧪 **Testing Scenarios**

### **Scenario 1: Camera on Same Network**
```
1. Start IP Webcam on phone (192.168.137.254)
2. Start backend: python app_simple.py
3. Wait 30 seconds for scan
4. Check dashboard: Should show camera as ONLINE
```

### **Scenario 2: Camera on Different Network**
```
1. Start IP Webcam on phone (192.168.1.100 - different network)
2. Backend shows camera as OFFLINE
3. Dashboard displays red status indicator
```

### **Scenario 3: Camera Goes Offline**
```
1. Camera initially ONLINE
2. Turn off phone / disconnect from WiFi
3. Within 30 seconds, status updates to OFFLINE
4. Dashboard shows last seen time
```

### **Scenario 4: New Camera Joins Network**
```
1. System running with 1 camera
2. Start second IP Webcam on new phone
3. Within 5 minutes, new camera discovered
4. Dashboard shows 2 cameras
```

---

## 🔧 **Manual Configuration**

If auto-discovery doesn't work, you can manually add cameras:

### **Using API:**
```bash
curl -X POST http://localhost:5000/api/camera/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My IP Webcam",
    "url": "http://192.168.137.254:8080/video",
    "type": "ip_webcam"
  }'
```

### **Using Dashboard:**
1. Click "Add Camera" button
2. Enter camera name and URL
3. Click "Save"
4. Camera appears in list

---

## 📁 **File Structure**

```
backend/
├── app/
│   └── services/
│       └── camera_discovery.py      # Auto-discovery service
├── storage/
│   └── database/
│       └── discovered_cameras.json  # Discovered cameras database
└── app_simple.py                    # API server with discovery
```

---

## 🐛 **Troubleshooting**

### **Problem: No cameras discovered**
**Solution:**
1. Check if IP Webcam is running on phone
2. Verify phone and computer on same WiFi network
3. Check firewall settings (allow port 8080)
4. Manually trigger scan: `POST /api/camera/scan`

### **Problem: Camera shows OFFLINE but it's ON**
**Solution:**
1. Check camera URL is correct
2. Verify network connectivity: `ping <camera-ip>`
3. Test camera URL in browser: `http://<camera-ip>:8080/video`
4. Wait 30 seconds for status update

### **Problem: Camera not auto-discovered**
**Solution:**
1. Check if camera uses non-standard port
2. Manually add camera using API or dashboard
3. Check if camera requires authentication
4. Verify camera is on same subnet

---

## ✅ **Success Indicators**

### **Console Output:**
```
🔍 Starting camera discovery service...
🌐 Performing initial network scan...
📍 Local IP: 192.168.137.1
🔍 Scanning network 192.168.137.0/24 for cameras...
📱 Found IP Webcam at 192.168.137.254:8080
💾 Saved 1 discovered cameras
✅ Scan complete. Found 1 cameras
✅ Camera discovery service started
🚀 Background camera scanning started (interval: 300s)
🚀 Camera status monitoring started (interval: 30s)
```

### **Dashboard:**
```
Active Cameras: 1 (was 0)
System Online (was offline)
Camera card shows: 🟢 ONLINE
```

---

## 🎯 **Next Steps**

1. ✅ Start backend: `python app_simple.py`
2. ✅ Wait 30 seconds for initial scan
3. ✅ Check dashboard at `http://localhost:3000/dashboard`
4. ✅ Verify camera count and status
5. ✅ Test by disconnecting/reconnecting camera

---

**Date:** October 17, 2025  
**Status:** ✅ Implemented and ready to test  
**Features:** Auto-discovery | Network monitoring | ONLINE/OFFLINE status | Manual add/remove
