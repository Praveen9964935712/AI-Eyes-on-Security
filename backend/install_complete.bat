@echo off
echo ==================================================
echo AI Eyes Security System - Complete Installation
echo ==================================================
echo.

echo Step 1: Setting up Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)

echo Step 5: Running setup script...
python setup.py

echo Step 6: Installing frontend dependencies...
cd ..
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    cd backend
    pause
    exit /b 1
)

cd backend

echo.
echo ==================================================
echo Installation completed successfully!
echo ==================================================
echo.
echo Next steps:
echo 1. Configure your settings in backend\.env file
echo 2. Add known faces to backend\data\known_faces\
echo 3. Set up email credentials for alerts
echo 4. Start the system:
echo    - Backend: run start_backend.bat
echo    - Frontend: npm run dev
echo.
echo For detailed instructions, see README.md
echo.
pause