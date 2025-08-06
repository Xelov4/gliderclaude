# Script PowerShell de démarrage avec configuration ccache automatique
# Pour l'application Poker AI MVP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration ccache pour Poker AI MVP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Vérifier si ccache est disponible
try {
    $ccacheVersion = & ccache --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ccache est disponible" -ForegroundColor Green
        Write-Host "Version: $($ccacheVersion[0].Split()[2])" -ForegroundColor Gray
    } else {
        throw "ccache non trouvé"
    }
} catch {
    Write-Host "⚠️  ccache n'est pas trouvé dans le PATH" -ForegroundColor Yellow
    Write-Host "Ajout de ccache au PATH..." -ForegroundColor Yellow
    $env:PATH += ";C:\ccache\ccache-4.11.3-windows-x86_64"
}

# Configurer ccache
Write-Host "Configuration de ccache..." -ForegroundColor Cyan
& ccache --set-config=cache_dir=C:\ccache\cache 2>$null
& ccache --set-config=max_size=5G 2>$null

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Vérifier les dépendances
Write-Host "Vérification des dépendances..." -ForegroundColor Cyan
try {
    $paddleTest = & python -c "import paddle; print('✅ Paddle disponible')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Paddle disponible" -ForegroundColor Green
    } else {
        throw "Paddle non disponible"
    }
} catch {
    Write-Host "❌ Paddle n'est pas disponible, installation..." -ForegroundColor Red
    & pip install paddlepaddle setuptools
}

# Démarrer l'application
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage de l'application Poker AI MVP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "L'application va maintenant démarrer sans avertissements ccache." -ForegroundColor Green
Write-Host ""

& python run.py 