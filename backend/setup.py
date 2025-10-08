import os
import sys
import json
from datetime import datetime

def create_sample_known_faces():
    """Create sample known faces directory structure"""
    known_faces_dir = "data/known_faces"
    
    # Create directories for sample people
    sample_people = ["farmer_john", "owner_smith", "manager_alice"]
    
    for person in sample_people:
        person_dir = os.path.join(known_faces_dir, person)
        os.makedirs(person_dir, exist_ok=True)
        
        # Create a readme file with instructions
        readme_content = f"""
# Known Person: {person.replace('_', ' ').title()}

## Instructions:
1. Add 5-10 clear photos of this person to this directory
2. Photos should be well-lit with the person facing the camera
3. Include different angles and expressions
4. Supported formats: .jpg, .jpeg, .png
5. Recommended image size: 640x480 or higher

## Photo naming convention:
- {person}_1.jpg
- {person}_2.jpg
- etc.

## Training:
The system will automatically retrain the face recognition model when new photos are added.
"""
        
        with open(os.path.join(person_dir, "README.md"), "w") as f:
            f.write(readme_content)

def create_sample_config():
    """Create sample configuration files"""
    config_data = {
        "system": {
            "mode": "farm",  # or "bank"
            "auto_training": True,
            "save_detections": True,
            "max_storage_days": 30
        },
        "cameras": [
            {
                "id": 1,
                "name": "Farm Gate A",
                "location": "Main Entrance", 
                "url": "0",  # Default camera
                "type": "farm",
                "ai_model": "face_recognition",
                "enabled": True
            },
            {
                "id": 2,
                "name": "IP Camera Test",
                "location": "Test Location",
                "url": "http://192.168.1.100:8080/video",
                "type": "farm", 
                "ai_model": "face_recognition",
                "enabled": False
            }
        ],
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email_address": "your-email@gmail.com",
            "email_password": "your-app-password",
            "recipients": ["admin@yourdomain.com"]
        },
        "detection": {
            "face_recognition_threshold": 0.6,
            "suspicious_activity_threshold": 0.7,
            "detection_confidence": 0.5,
            "detection_fps": 10
        }
    }
    
    config_path = "config/system_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Created configuration file: {config_path}")

def create_env_template():
    """Create .env template file"""
    env_content = """# AI Eyes Security System Configuration
# Copy this to .env and update with your settings

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email Configuration (for alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
ALERT_RECIPIENTS=admin@yourdomain.com

# Camera Configuration
DEFAULT_CAMERA_URL=0
CAMERA_RESOLUTION_WIDTH=640
CAMERA_RESOLUTION_HEIGHT=480
FPS=30

# AI Model Configuration
FACE_RECOGNITION_THRESHOLD=0.6
SUSPICIOUS_ACTIVITY_THRESHOLD=0.7
DETECTION_CONFIDENCE=0.5

# Paths (relative to backend directory)
KNOWN_FACES_PATH=data/known_faces
ALERTS_PATH=data/alerts
MODELS_PATH=app/ai_models

# System Configuration
DEFAULT_MODE=farm
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    
    print("Created .env.template file")

def create_installation_script():
    """Create installation script"""
    install_script = """@echo off
echo Installing AI Eyes Security System...

echo.
echo Step 1: Installing Python packages...
pip install -r requirements.txt

echo.
echo Step 2: Creating directories...
mkdir data\\known_faces 2>nul
mkdir data\\alerts 2>nul
mkdir config 2>nul
mkdir app\\ai_models 2>nul

echo.
echo Step 3: Setting up configuration...
python setup.py

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Copy .env.template to .env and configure your settings
echo 2. Add known faces to data/known_faces/ directories
echo 3. Configure email settings in .env file
echo 4. Run the system with: python app.py
echo.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(install_script)
    
    print("Created install.bat script")

def create_startup_scripts():
    """Create startup scripts"""
    
    # Windows batch script
    windows_script = """@echo off
title AI Eyes Security System
echo Starting AI Eyes Security System...
echo.

REM Check if virtual environment exists
if exist "venv\\Scripts\\activate.bat" (
    echo Activating virtual environment...
    call venv\\Scripts\\activate.bat
)

REM Start the Flask backend
echo Starting backend server...
python app.py

pause
"""
    
    with open("start_backend.bat", "w") as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    linux_script = """#!/bin/bash
echo "Starting AI Eyes Security System..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the Flask backend
echo "Starting backend server..."
python app.py
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(linux_script)
    
    # Make shell script executable
    os.chmod("start_backend.sh", 0o755)
    
    print("Created startup scripts")

def create_readme():
    """Create comprehensive README"""
    readme_content = """# AI Eyes Security System 🔍

A smart surveillance system using Deep Learning for real-time threat detection.

## 🚀 Features

- **Face Recognition** (LBPH) for farm security
- **Suspicious Activity Detection** (YOLOv9) for bank security  
- **Real-time AI Analysis** of video streams
- **Instant Email Alerts** with images
- **Web Dashboard** for monitoring and control
- **IP Webcam Support** for cost-effective deployment

## 📋 Requirements

- Python 3.8+
- OpenCV 4.8+
- Node.js 16+ (for frontend)
- Webcam or IP camera
- Email account for alerts (Gmail recommended)

## 🛠️ Installation

### Backend Setup

1. Clone the repository and navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\\Scripts\\activate

# Linux/Mac  
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Run setup script:
```bash
python setup.py
```

6. Configure environment:
```bash
copy .env.template .env
# Edit .env with your settings
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../
```

2. Install Node.js dependencies:
```bash
npm install
```

## 📁 Project Structure

```
AI eyes/
├── backend/
│   ├── app/
│   │   ├── ai_models/          # AI detection models
│   │   ├── routes/             # API endpoints
│   │   ├── services/           # Business logic
│   │   └── utils/              # Helper functions
│   ├── config/                 # Configuration files
│   ├── data/
│   │   ├── known_faces/        # Known person photos
│   │   └── alerts/             # Alert images/videos
│   ├── app.py                  # Main Flask application
│   └── requirements.txt        # Python dependencies
├── src/                        # React frontend
├── package.json               # Node.js dependencies
└── README.md
```

## 🔧 Configuration

### Known Faces Setup (Farm Mode)

1. Navigate to `backend/data/known_faces/`
2. Create folders for each known person (e.g., `farmer_john/`)
3. Add 5-10 clear photos of each person
4. System will auto-train on startup

### Email Alerts Setup

1. Edit `backend/.env` file:
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
ALERT_RECIPIENTS=admin@yourdomain.com
```

2. For Gmail, create an App Password:
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate App Password for "Mail"
   - Use this password in .env file

### Camera Setup

- **Local Camera**: Set `DEFAULT_CAMERA_URL=0`
- **IP Webcam**: Set `DEFAULT_CAMERA_URL=http://192.168.1.100:8080/video`

## 🚀 Running the System

### Start Backend Server
```bash
cd backend
python app.py
```

### Start Frontend Development Server
```bash
npm run dev
```

### Access the Dashboard
- Open browser to `http://localhost:5173`
- Backend API runs on `http://localhost:5000`

## 🔍 Usage

### Farm Security Mode
1. Add photos of authorized personnel to `data/known_faces/`
2. Set system mode to "farm" in configuration
3. System alerts on unknown faces

### Bank Security Mode  
1. Set system mode to "bank" in configuration
2. System detects weapons and suspicious activities
3. Monitors for armed threats and crowd formations

## 📊 Monitoring

- **Live Streams**: View all camera feeds
- **Alerts**: Review security alerts with images
- **Event Logs**: Track all detection events
- **Statistics**: Monitor system performance

## 🚨 Alert Types

- **Intruder Detection**: Unknown person in farm mode
- **Suspicious Activity**: Unusual behavior patterns
- **Weapon Detection**: Firearms or weapons detected  
- **Armed Threat**: Person with weapon detected

## 📧 Email Notifications

Automatic email alerts include:
- Alert type and severity
- Location and timestamp
- Confidence score
- Captured image
- Immediate action recommendations

## 🔧 Troubleshooting

### Common Issues

1. **Camera not detected**:
   - Check camera permissions
   - Try different camera indices (0, 1, 2...)
   - Verify IP camera URL

2. **Email alerts not working**:
   - Check email credentials in .env
   - Verify App Password for Gmail
   - Check firewall/antivirus settings

3. **Face recognition not working**:
   - Add more photos to known_faces directories
   - Ensure photos are clear and well-lit
   - Check face detection in logs

4. **High CPU usage**:
   - Reduce detection FPS in configuration
   - Lower camera resolution
   - Close unnecessary applications

## 📈 Performance Tips

- Use lower resolution for real-time processing
- Reduce detection FPS if CPU usage is high
- Add more photos for better face recognition
- Use SSD storage for faster image processing

## 🔒 Security Notes

- Keep .env file secure and never commit to version control
- Use strong passwords for email accounts
- Regularly update dependencies
- Monitor system logs for suspicious activities

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review system logs
3. Verify configuration settings
4. Contact system administrator

## 📄 License

This project is for educational and research purposes.

---

**AI Eyes Security System** - Enhancing security through intelligent surveillance 🔍🛡️
"""
    
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created comprehensive README.md")

def main():
    """Main setup function"""
    print("Setting up AI Eyes Security System...")
    print("=" * 50)
    
    # Create necessary directories
    directories = [
        "data/known_faces",
        "data/alerts", 
        "config",
        "app/ai_models"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create sample configurations and files
    create_sample_known_faces()
    create_sample_config()
    create_env_template()
    create_installation_script()
    create_startup_scripts()
    create_readme()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.template to .env and configure your settings")
    print("2. Add known faces to data/known_faces/ directories")
    print("3. Configure email settings for alerts")
    print("4. Run: python app.py")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()