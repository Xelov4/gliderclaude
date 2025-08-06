@echo off
REM Script to fix OCR dependencies for Poker AI MVP
REM This script reinstalls PaddleOCR with the correct version

echo ========================================
echo Fixing OCR Dependencies for Poker AI MVP
echo ========================================

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Uninstall current PaddleOCR
echo Uninstalling current PaddleOCR...
pip uninstall paddleocr -y

REM Install the correct version
echo Installing PaddleOCR version 2.7.0.3...
pip install paddleocr==2.7.0.3

REM Install additional dependencies that might be missing
echo Installing additional OCR dependencies...
pip install paddlepaddle
pip install opencv-python
pip install Pillow

REM Verify installation
echo ========================================
echo Verifying OCR installation...
echo ========================================
python -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR imported successfully')"
python -c "import cv2; print('✅ OpenCV imported successfully')"
python -c "from PIL import Image; print('✅ Pillow imported successfully')"

echo ========================================
echo OCR dependencies fixed successfully!
echo ========================================
echo.
echo You can now run the application with:
echo start_with_ccache.bat
echo.

pause 