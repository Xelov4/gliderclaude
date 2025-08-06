@echo off
REM Script de démarrage avec configuration ccache automatique
REM Pour l'application Poker AI MVP

echo ========================================
echo Configuration ccache pour Poker AI MVP
echo ========================================

REM Vérifier si ccache est disponible
where ccache >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  ccache n'est pas trouvé dans le PATH
    echo Ajout de ccache au PATH...
    set "PATH=%PATH%;C:\ccache\ccache-4.11.3-windows-x86_64"
)

REM Configurer ccache si nécessaire
echo Configuration de ccache...
ccache --set-config=cache_dir=C:\ccache\cache >nul 2>&1
ccache --set-config=max_size=5G >nul 2>&1

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier les dépendances OCR
echo Vérification des dépendances OCR...
py -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR disponible')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PaddleOCR n'est pas disponible, installation...
    pip install paddleocr==2.7.0.3
    pip install paddlepaddle
)

REM Vérifier les dépendances
echo Vérification des dépendances...
py -c "import paddle; print('✅ Paddle disponible')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Paddle n'est pas disponible, installation...
    pip install paddlepaddle setuptools
)

REM Tester le système OCR
echo Test du système OCR...
py test_ocr.py
if %errorlevel% neq 0 (
    echo ⚠️  Tests OCR échoués, mais l'application peut continuer avec le système de fallback
)

REM Démarrer l'application
echo ========================================
echo Démarrage de l'application Poker AI MVP
echo ========================================
echo.
echo L'application va maintenant démarrer avec le système OCR corrigé.
echo.
py run.py

pause 