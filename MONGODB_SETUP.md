# MongoDB Setup for AI Eyes Security System

## Quick MongoDB Installation (Windows)

### Option 1: MongoDB Community Server (Recommended)
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. Choose "Complete" installation
4. Install MongoDB as a Windows Service
5. MongoDB will run automatically on port 27017

### Option 2: MongoDB with Docker (Alternative)
```bash
# Install Docker Desktop first, then run:
docker run --name mongodb -d -p 27017:27017 mongo:latest
```

### Option 3: MongoDB Atlas (Cloud)
1. Create free account at: https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string and update MONGODB_URL in backend/database/config.py

## Verification
Once MongoDB is installed, you can verify it's running:
```bash
# Open Command Prompt and run:
mongosh
# You should see MongoDB shell connection
```

## System Features

### With MongoDB (Full Features):
- ✅ Persistent camera storage
- ✅ Alert history and tracking
- ✅ System logs and analytics
- ✅ Performance monitoring
- ✅ Advanced queries and reports

### Without MongoDB (Fallback Mode):
- ✅ Basic camera management (session-based)
- ✅ Live video streaming
- ✅ Real-time monitoring
- ✅ Image snapshots to local storage
- ⚠️ Data resets on server restart

## Current Status
The system automatically detects MongoDB availability and falls back to in-memory storage if needed. All features work in both modes, but data persistence requires MongoDB.

## Storage Features (Work without MongoDB)
- 📸 Camera snapshots saved to: `backend/storage/snapshots/`
- 🚨 Alert images saved to: `backend/storage/alerts/`
- 📹 Recordings saved to: `backend/storage/recordings/`
- 🗃️ Automatic cleanup of old files
- 📊 Storage statistics and monitoring