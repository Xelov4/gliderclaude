@echo off
REM Script de démarrage avec OCR fallback pour Poker AI MVP
REM Ce script évite les problèmes de compatibilité Python 3.13

echo ========================================
echo Démarrage Poker AI MVP avec OCR Fallback
echo ========================================

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier les dépendances de base
echo Vérification des dépendances de base...
py -c "import loguru; print('✅ Loguru disponible')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Loguru manquant, installation...
    pip install loguru
)

REM Tester le système OCR de base
echo Test du système OCR de base...
py -c "import sys; sys.path.append('src'); from src.vision.ocr import TextRecognizer; r = TextRecognizer(); print('✅ OCR system ready')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  OCR system not fully functional, but fallback will work
)

REM Démarrer l'application
echo ========================================
echo Démarrage de l'application Poker AI MVP
echo ========================================
echo.
echo L'application va démarrer avec le système OCR de fallback.
echo Le système fournira des données réalistes pour les tests.
echo.
py run.py

pause 