@echo off
echo ========================================
echo Poker AI MVP - Setup and Run
echo ========================================
echo.

cd /d "C:\Users\McGrady\Desktop\yes\poker_ai_mvp"

echo Setting up Python virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python 3.11+ is installed
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Poker AI MVP...
echo ========================================
echo.

python run.py

echo.
echo Application closed.
pause