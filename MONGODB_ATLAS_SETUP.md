# MongoDB Atlas Setup Guide for AI Eyes Security System

## Quick Setup Steps:

### 1. Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/atlas
2. Click "Try Free" and create an account
3. Choose "Shared" (Free tier - M0)
4. Select a cloud provider and region (choose closest to you)
5. Create cluster (usually takes 1-3 minutes)

### 2. Database Access Setup
1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `ai_eyes_user`
5. Password: Generate a secure password (save this!)
6. Database User Privileges: "Read and write to any database"
7. Click "Add User"

### 3. Network Access Setup
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for development)
4. Or add your specific IP address for security
5. Click "Confirm"

### 4. Get Connection String
1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" and version "3.6 or later"
5. Copy the connection string (looks like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### 5. Update Your Application
Replace `<username>` and `<password>` in the connection string, then update your environment variable.

## Environment Variable Setup:

### Option 1: Create .env file (Recommended)
Create a file called `.env` in your backend folder:
```
MONGODB_URL=mongodb+srv://ai_eyes_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ai_eyes_security?retryWrites=true&w=majority
DATABASE_NAME=ai_eyes_security
```

### Option 2: Windows Environment Variable
```cmd
setx MONGODB_URL "mongodb+srv://ai_eyes_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ai_eyes_security?retryWrites=true&w=majority"
```

## Security Notes:
- Never commit connection strings with passwords to version control
- Use specific IP addresses instead of "Allow Access from Anywhere" in production
- Enable MongoDB Atlas security features for production use
- Consider using MongoDB Atlas App Services for additional security

## Free Tier Limits:
- 512 MB storage
- 100 connections
- No backup snapshots
- Perfect for development and small applications

Your AI Eyes Security System will automatically detect the MongoDB connection and switch from fallback mode to full database functionality!