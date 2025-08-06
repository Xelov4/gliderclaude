@echo off
echo ========================================
echo   Poker AI MVP - Python Setup Script
echo ========================================
echo.

echo Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found!
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found! Version:
py --version

echo.
echo Creating virtual environment...
py -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
py -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo To activate the environment manually:
echo   call venv\Scripts\activate.bat
echo.
echo To run the application:
echo   python run.py
echo.
pause