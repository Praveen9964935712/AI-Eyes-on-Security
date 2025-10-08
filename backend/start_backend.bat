@echo off
title AI Eyes Security System
echo Starting AI Eyes Security System...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the Flask backend
echo Starting backend server...
python app.py

pause
