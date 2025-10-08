# AI Eyes Security System 🔍

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
venv\Scripts\activate

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
