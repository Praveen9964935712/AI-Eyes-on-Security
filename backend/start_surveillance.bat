@echo off
REM Quick Start Script for AI Eyes Surveillance System

echo 🔍 AI Eyes - Smart Surveillance System
echo =======================================

REM Check if we're in the right directory
if not exist "multi_camera_surveillance.py" (
    echo ❌ Please run this script from the backend directory
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found

REM Install requirements if needed
if not exist ".venv" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
) else (
    echo ✅ Dependencies already installed
)

echo.
echo 🚀 Starting Multi-Camera AI Surveillance...
echo 🌐 Dashboard will be available at: http://localhost:5002
echo ⚠️  Press Ctrl+C to stop
echo.

REM Start the surveillance system
python multi_camera_surveillance.py

pause