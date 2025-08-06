@echo off
echo ========================================
echo   Poker AI MVP - Complete Setup & Run
echo ========================================
echo.

echo Step 1: Setting up Python environment...
call setup_python.bat
if %errorlevel% neq 0 (
    echo Python setup failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Setting up YOLO model (optional)...
echo You can press Ctrl+C to skip model setup and run basic version
python setup_cards_model.py

echo.
echo Step 4: Starting Poker AI MVP...
echo.
echo Dashboard will open shortly...
echo Use the GUI to calibrate regions and start vision system
echo.
python run.py

pause