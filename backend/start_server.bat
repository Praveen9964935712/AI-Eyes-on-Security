@echo off
echo ========================================
echo AI Eyes Security System - Backend Server
echo ========================================
echo.
echo Starting backend server on port 8000...
echo MongoDB: Will auto-detect Atlas or local
echo Storage: Local filesystem enabled
echo.
cd /d "C:\Users\prave\OneDrive\Desktop\AI eyes\backend"

REM Check if .env file exists
if exist .env (
    echo ✅ Found .env configuration file
) else (
    echo ⚠️  No .env file found - using default settings
    echo 💡 Run: python setup_mongodb.py to configure MongoDB Atlas
)
echo.

REM Start the server
python -m flask --app app_simple run --host=0.0.0.0 --port=8000 --debug

echo.
echo Server stopped. Press any key to exit...
pause