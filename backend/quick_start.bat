@echo off
echo ==========================================
echo   AI Eyes Security System - Quick Start
echo ==========================================
echo.

echo Setting up Python environment...
cd /d "%~dp0"

echo Starting backend server...
echo Open another terminal and run 'npm run dev' for frontend
echo Dashboard will be available at: http://localhost:5173
echo.

"C:/Users/prave/OneDrive/Desktop/AI eyes/.venv/Scripts/python.exe" app.py

pause