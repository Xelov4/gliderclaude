@echo off
REM Script pour configurer Python 3.11 pour OCR complet
REM Python 3.13 a des problèmes de compatibilité avec numpy/opencv

echo ========================================
echo Configuration Python 3.11 pour OCR complet
echo ========================================

echo.
echo ⚠️  ATTENTION: Ce script nécessite Python 3.11 installé
echo.
echo Étapes recommandées:
echo 1. Télécharger Python 3.11 depuis python.org
echo 2. Installer Python 3.11 dans un dossier séparé
echo 3. Créer un nouvel environnement virtuel avec Python 3.11
echo 4. Réinstaller les dépendances
echo.

echo Voulez-vous continuer avec Python 3.11? (O/N)
set /p choice=

if /i "%choice%"=="O" (
    echo Configuration Python 3.11...
    
    REM Vérifier si Python 3.11 est disponible
    py -3.11 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python 3.11 non trouvé
        echo Veuillez installer Python 3.11 depuis python.org
        pause
        exit /b 1
    )
    
    echo ✅ Python 3.11 trouvé
    echo Création d'un nouvel environnement virtuel...
    
    REM Créer un nouvel environnement virtuel
    py -3.11 -m venv venv311
    
    echo Activation de l'environnement Python 3.11...
    call venv311\Scripts\activate.bat
    
    echo Installation des dépendances OCR...
    pip install -r requirements.txt
    
    echo ✅ Environnement Python 3.11 configuré
    echo Vous pouvez maintenant utiliser: venv311\Scripts\python.exe
) else (
    echo Configuration annulée
)

pause 