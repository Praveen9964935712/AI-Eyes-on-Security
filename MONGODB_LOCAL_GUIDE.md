# 🔧 MongoDB Local Installation Guide

## ❌ **Problem: MongoDB Atlas SSL Issues**

Your MongoDB Atlas connection fails due to:
- **SSL/TLS handshake errors** (Python 3.13 + Windows SSL compatibility)
- Network/firewall restrictions
- MongoDB Atlas SSL certificate validation issues

## ✅ **Solution: Use Local MongoDB (Recommended)**

### **Option 1: Install MongoDB Community Server (Best)**

#### **Step 1: Download MongoDB**
1. Go to: https://www.mongodb.com/try/download/community
2. Version: **8.0.4** (Current)
3. Platform: **Windows x64**
4. Package: **MSI**
5. Click **Download**

#### **Step 2: Install MongoDB**
1. Run the downloaded `.msi` file
2. Choose **Complete** installation
3. ✅ Check "Install MongoDB as a Service"
4. ✅ Check "Run service as Network Service user"
5. ✅ Uncheck "Install MongoDB Compass" (optional GUI, not needed)
6. Click **Install**

#### **Step 3: Start MongoDB Service**
```powershell
# Start MongoDB service
net start MongoDB

# Verify it's running
Get-Service MongoDB
```

#### **Step 4: Update Your .env File**
```env
# Change this line:
# MONGODB_URL=mongodb+srv://praveenkumarnaik14_db_user:qnwUOOrDJ0RgBwp7@cluster0.7gifool.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# To this:
MONGODB_URL=mongodb://localhost:27017/
```

#### **Step 5: Test Connection**
```bash
cd backend
python mongodb_setup.py
```

Expected output:
```
✅ MongoDB Atlas Connection Successful!
📊 Database: ai_eyes_security
🎉 All tests passed! MongoDB is ready to use!
```

---

### **Option 2: Use JSON Storage (Current - Works Great!)**

**No installation needed!** Your system already works perfectly with JSON files.

#### **Advantages:**
- ✅ No external dependencies
- ✅ No installation required
- ✅ Faster startup
- ✅ No SSL issues
- ✅ Easy to backup (just copy files)
- ✅ Easy to debug (readable text files)

#### **Storage Location:**
```
backend/storage/database/
├── alerts.json           # All alerts
├── cameras.json          # Camera configs
├── logs.json             # System logs
└── discovered_cameras.json  # Auto-discovered cameras
```

#### **Performance:**
- Handles **1000s of records** easily
- Perfect for farm surveillance (< 100 cameras)
- Instant startup
- No network dependencies

---

### **Option 3: Fix MongoDB Atlas (Advanced)**

If you really want MongoDB Atlas, try these fixes:

#### **Fix 1: Whitelist IP Address**
1. Login to MongoDB Atlas: https://cloud.mongodb.com/
2. Click **Network Access**
3. Click **Add IP Address**
4. Click **Allow Access from Anywhere** (0.0.0.0/0)
5. Wait 3-5 minutes

#### **Fix 2: Downgrade Python SSL**
```powershell
pip install "pymongo[srv]<4.0" certifi
```

#### **Fix 3: Use MongoDB Atlas Connection String without +srv**
Get the standard connection string (not srv) from Atlas:
```
mongodb://user:pass@ac-jrk6ytx-shard-00-00.7gifool.mongodb.net:27017,ac-jrk6ytx-shard-00-01.7gifool.mongodb.net:27017,ac-jrk6ytx-shard-00-02.7gifool.mongodb.net:27017/?ssl=true&replicaSet=atlas-xxxxx-shard-0
```

---

## 🎯 **My Recommendation**

### **For Your Use Case (Farm Surveillance):**

**Keep using JSON Storage!**

**Why?**
- ✅ Already working perfectly
- ✅ No setup required
- ✅ No SSL headaches
- ✅ Sufficient for your needs
- ✅ Easier to maintain

**When to use MongoDB:**
- You have 100+ cameras
- You need complex queries
- You want cloud backup
- You have millions of records

**Your current scale:**
- 1-10 cameras ✅ JSON is perfect
- < 1000 alerts/day ✅ JSON is perfect
- Single farm location ✅ JSON is perfect

---

## 🚀 **Quick Decision Guide**

| Feature | JSON Storage | Local MongoDB | MongoDB Atlas |
|---------|--------------|---------------|---------------|
| **Setup Time** | ⚡ 0 minutes | 🕐 5 minutes | 🕐 10 minutes |
| **Cost** | ✅ Free | ✅ Free | ⚠️ Free tier limited |
| **Speed** | ⚡ Fastest | 🚀 Fast | 🐌 Network dependent |
| **Reliability** | ✅ Always works | ✅ Always works | ⚠️ Network issues |
| **SSL Issues** | ✅ None | ✅ None | ❌ Your current problem |
| **Backup** | ✅ Copy files | 🔧 Export/Import | ✅ Automatic |
| **Your Case** | ✅ **RECOMMENDED** | ✅ Optional | ⚠️ Overkill |

---

## ✅ **Final Recommendation**

**Keep JSON storage!** Your system works great with it!

**If you still want MongoDB:**
1. Install MongoDB Community Server locally (5 minutes)
2. Change `.env`: `MONGODB_URL=mongodb://localhost:27017/`
3. Restart backend

**No need for MongoDB Atlas - local MongoDB is easier and faster!**

---

**Date:** October 17, 2025  
**Status:** JSON storage working ✅  
**Recommendation:** Keep JSON or install local MongoDB  
**Avoid:** MongoDB Atlas (SSL issues with Python 3.13)
