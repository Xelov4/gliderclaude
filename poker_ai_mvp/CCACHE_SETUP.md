# Configuration ccache pour Poker AI MVP

## Problème résolu

L'application affichait un avertissement lors du démarrage :
```
No ccache found. Please be aware that recompiling all source files may be required.
```

Ce message ralentissait l'application car Paddle devait recompiler des fichiers source à chaque démarrage.

## Solution implémentée

### 1. Installation de ccache

ccache a été installé depuis GitHub :
- **Version** : 4.11.3
- **Emplacement** : `C:\ccache\ccache-4.11.3-windows-x86_64\ccache.exe`
- **Cache** : `C:\ccache\cache`
- **Taille maximale** : 5 GB

### 2. Configuration automatique

Le PATH a été mis à jour pour inclure ccache :
```
PATH += C:\ccache\ccache-4.11.3-windows-x86_64
```

### 3. Scripts de démarrage

Deux scripts de démarrage ont été créés :

#### Script Batch (Windows)
```bash
start_with_ccache.bat
```

#### Script PowerShell (Windows)
```powershell
start_with_ccache.ps1
```

Ces scripts :
- Vérifient la disponibilité de ccache
- Configurent automatiquement le cache
- Activent l'environnement virtuel
- Vérifient les dépendances
- Démarrent l'application

### 4. Test de configuration

Un script de test est disponible :
```bash
python test_ccache.py
```

Ce script vérifie :
- ✅ Disponibilité de ccache
- ✅ Configuration du cache
- ✅ Import de Paddle sans avertissements

## Utilisation

### Démarrage rapide
```bash
# Avec PowerShell (recommandé)
.\start_with_ccache.ps1

# Avec Batch
.\start_with_ccache.bat
```

### Démarrage manuel
```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Vérifier ccache
ccache --version

# Démarrer l'application
python run.py
```

## Vérification

Pour vérifier que tout fonctionne correctement :

1. **Test de ccache** :
   ```bash
   ccache --version
   ccache --show-config
   ccache --show-stats
   ```

2. **Test de Paddle** :
   ```bash
   python -c "import paddle; print('✅ Paddle importé sans avertissements')"
   ```

3. **Test complet** :
   ```bash
   python test_ccache.py
   ```

## Avantages

- ✅ **Plus d'avertissements** lors du démarrage
- ✅ **Démarrage plus rapide** grâce au cache
- ✅ **Configuration automatique** via les scripts
- ✅ **Vérification facile** avec le script de test

## Dépannage

### Si ccache n'est pas trouvé
```bash
# Vérifier le PATH
echo $env:PATH

# Ajouter manuellement
$env:PATH += ";C:\ccache\ccache-4.11.3-windows-x86_64"
```

### Si Paddle ne s'importe pas
```bash
# Réinstaller les dépendances
pip install paddlepaddle setuptools
```

### Si le cache est corrompu
```bash
# Nettoyer le cache
ccache --clear
```

## Fichiers créés

- `C:\ccache\` - Répertoire d'installation de ccache
- `C:\ccache\cache\` - Répertoire de cache
- `start_with_ccache.bat` - Script de démarrage Batch
- `start_with_ccache.ps1` - Script de démarrage PowerShell
- `test_ccache.py` - Script de test de configuration
- `CCACHE_SETUP.md` - Cette documentation 