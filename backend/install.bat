@echo off
echo Installing AI Eyes Security System...

echo.
echo Step 1: Installing Python packages...
pip install -r requirements.txt

echo.
echo Step 2: Creating directories...
mkdir data\known_faces 2>nul
mkdir data\alerts 2>nul
mkdir config 2>nul
mkdir app\ai_models 2>nul

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
