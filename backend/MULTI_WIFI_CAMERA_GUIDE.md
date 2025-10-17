# Multi-WiFi Camera Setup Guide 🎥

## Your Scenario

You have **2 IP Webcams on different WiFi networks**:
1. **Car WiFi Camera** (e.g., 192.168.137.254:8080)
2. **Home WiFi Camera** (e.g., 192.168.1.100:8080)

You want **both cameras to be visible** in Live Camera Streams regardless of which WiFi you're connected to.

## How It Works Now ✅

### Current System Behavior:

1. **Cameras Stored in MongoDB**
   - Once added, cameras persist permanently
   - No auto-discovery (manual control only)
   - Status monitored every 30 seconds

2. **Status Monitoring**
   - **ONLINE**: Camera responds (same network)
   - **OFFLINE**: Camera unreachable (different network)

3. **Frontend Display**
   - Shows ALL cameras from MongoDB
   - Color-coded status (green=online, red=offline)

### What Happens When You Switch Networks:

**Scenario 1: Connected to Car WiFi**
```
🟢 Car WiFi Camera (192.168.137.254) - ONLINE
🔴 Home WiFi Camera (192.168.1.100) - OFFLINE
```

**Scenario 2: Connected to Home WiFi**
```
🔴 Car WiFi Camera (192.168.137.254) - OFFLINE
🟢 Home WiFi Camera (192.168.1.100) - ONLINE
```

Both cameras **always visible**, status updates automatically!

## How to Add Your Cameras

### Method 1: Using the Script (Easiest)

1. **Edit the script** `add_cameras_manual.py`:
   ```python
   # Change these IPs to your actual camera IPs
   add_camera(
       name="Car WiFi Camera",
       ip="192.168.137.254",  # Your car WiFi IP
       port=8080,
       location='Car'
   )
   
   add_camera(
       name="Home WiFi Camera",
       ip="192.168.1.100",  # Your home WiFi IP
       port=8080,
       location='Home'
   )
   ```

2. **Run the script**:
   ```bash
   cd backend
   python add_cameras_manual.py
   ```

3. **Start backend**:
   ```bash
   python app_simple.py
   ```

### Method 2: Using API (Alternative)

**Add Car Camera:**
```bash
curl -X POST http://localhost:5000/api/camera/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Car WiFi Camera",
    "url": "http://192.168.137.254:8080/video",
    "type": "ip_webcam",
    "location": "Car"
  }'
```

**Add Home Camera:**
```bash
curl -X POST http://localhost:5000/api/camera/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home WiFi Camera",
    "url": "http://192.168.1.100:8080/video",
    "type": "ip_webcam",
    "location": "Home"
  }'
```

### Method 3: Using Frontend UI

1. Open dashboard: `http://localhost:3000`
2. Click **"+ Add Camera"** button
3. Fill in details for each camera
4. Click Save

## Admin Panel CRUD Operations ✅

Your system **already has** full CRUD operations in `camera_protected.py`:

### Available API Endpoints:

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/cameras` | List all cameras | Public |
| `GET` | `/api/cameras/<id>` | Get specific camera | Public |
| `POST` | `/api/cameras` | Create new camera | Admin |
| `PUT` | `/api/cameras/<id>` | Update camera | Admin |
| `DELETE` | `/api/cameras/<id>` | Delete camera | Admin |
| `POST` | `/api/cameras/<id>/enable` | Enable camera | Admin |
| `POST` | `/api/cameras/<id>/disable` | Disable camera | Admin |
| `POST` | `/api/cameras/bulk` | Bulk operations | Admin |

### Admin Authentication:

**Login to get token:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your_admin_password"}'
```

**Use token for admin operations:**
```bash
curl -X POST http://localhost:5000/api/cameras \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"name": "Camera 1", "url": "...", ...}'
```

## Camera Discovery Service ✅

Your `camera_discovery.py` already handles:

1. **MongoDB Storage** ✅
   - Cameras persist across restarts
   - No duplicates (checks by camera ID)

2. **Status Monitoring** ✅
   - Updates every 30 seconds
   - Sets online/offline based on connectivity

3. **Manual Addition** ✅
   - `add_manual_camera()` method
   - Creates unique ID: `camera_<ip>_<port>`

4. **Network-Independent** ✅
   - Cameras visible regardless of network
   - Status reflects current connectivity

## Example: Complete Workflow

### Step 1: Add Cameras (One Time)
```bash
# While on Car WiFi
python add_cameras_manual.py

# Output:
✅ Added: Car WiFi Camera (192.168.137.254:8080)
✅ Added: Home WiFi Camera (192.168.1.100:8080)

📊 Total Cameras: 2
🟢 Car WiFi Camera (ONLINE)
🔴 Home WiFi Camera (OFFLINE)
```

### Step 2: Start Backend
```bash
python app_simple.py

# Output:
📂 Loaded 2 previously discovered cameras from MongoDB
🔄 Updating camera connectivity status...
✅ Camera status updated
```

### Step 3: Switch to Home WiFi
```
# Status monitor automatically detects:
📊 Total Cameras: 2
🔴 Car WiFi Camera (OFFLINE)
🟢 Home WiFi Camera (ONLINE)
```

### Step 4: View in Dashboard
```
Open: http://localhost:3000/dashboard

Live Camera Streams:
┌─────────────────────┐  ┌─────────────────────┐
│ 🔴 Car WiFi Camera  │  │ 🟢 Home WiFi Camera │
│ OFFLINE             │  │ ONLINE              │
│ 192.168.137.254     │  │ 192.168.1.100       │
└─────────────────────┘  └─────────────────────┘
```

## Current API Routes

### Camera Routes (`camera.py`)
✅ `/api/camera/list` - Get all cameras with status
✅ `/api/camera/add` - Manually add camera
✅ `/api/camera/remove/<id>` - Remove camera
✅ `/api/camera/scan` - Trigger network scan
✅ `/api/camera/status` - Get discovery service status

### Protected Routes (`camera_protected.py`)
✅ `/api/cameras` (GET/POST) - CRUD operations
✅ `/api/cameras/<id>` (GET/PUT/DELETE) - Single camera
✅ `/api/cameras/<id>/enable` - Enable camera
✅ `/api/cameras/<id>/disable` - Disable camera
✅ `/api/cameras/bulk` - Bulk operations
✅ `/api/auth/login` - Admin authentication

## Summary

### ✅ What You Already Have:

1. **MongoDB Storage** - Cameras persist permanently
2. **Status Monitoring** - Auto-updates online/offline every 30s
3. **Manual Addition** - Add cameras via script/API/UI
4. **Admin CRUD** - Full create/read/update/delete operations
5. **Network-Independent** - Shows all cameras regardless of WiFi

### ✅ What Works:

- Add camera on Car WiFi → Saved to MongoDB
- Switch to Home WiFi → Car camera shows OFFLINE, Home shows ONLINE
- Both cameras visible in frontend
- Status updates automatically
- No duplicate documents created

### 🎯 Next Steps:

1. **Edit** `add_cameras_manual.py` with your actual IPs
2. **Run** `python add_cameras_manual.py`
3. **Start** `python app_simple.py`
4. **Open** `http://localhost:3000`
5. **See** both cameras in Live Camera Streams! 🎉

---

**Your system is already configured correctly!** Just add your cameras manually and they'll work across different WiFi networks. 🚀
