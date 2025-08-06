#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration de ccache
"""

import os
import subprocess
import sys

def test_ccache():
    """Test si ccache est disponible et configuré"""
    print("=== Test de configuration ccache ===")
    
    # Vérifier si ccache est dans le PATH
    try:
        result = subprocess.run(['ccache', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ccache est disponible")
            print(f"Version: {result.stdout.split()[2]}")
        else:
            print("❌ ccache n'est pas disponible")
            return False
    except FileNotFoundError:
        print("❌ ccache n'est pas trouvé dans le PATH")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de ccache: {e}")
        return False
    
    # Vérifier la configuration
    try:
        result = subprocess.run(['ccache', '--show-config'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Configuration ccache:")
            for line in result.stdout.split('\n'):
                if 'cache_dir' in line or 'max_size' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Impossible de récupérer la configuration ccache")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la configuration: {e}")
    
    # Vérifier les statistiques
    try:
        result = subprocess.run(['ccache', '--show-stats'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Statistiques ccache:")
            for line in result.stdout.split('\n'):
                if 'cache hit rate' in line or 'cache miss' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Impossible de récupérer les statistiques ccache")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des statistiques: {e}")
    
    return True

def test_paddle_import():
    """Test l'import de paddle sans avertissement ccache"""
    print("\n=== Test d'import paddle ===")
    
    try:
        # Rediriger stderr pour capturer les avertissements
        result = subprocess.run([sys.executable, '-c', 
                               'import paddle; print("Paddle importé avec succès")'],
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Paddle importé avec succès")
            
            # Vérifier s'il y a des avertissements ccache
            if 'ccache' in result.stderr.lower():
                print("⚠️  Avertissements ccache détectés:")
                for line in result.stderr.split('\n'):
                    if 'ccache' in line.lower():
                        print(f"   {line.strip()}")
            else:
                print("✅ Aucun avertissement ccache détecté")
            
            return True
        else:
            print(f"❌ Erreur lors de l'import de paddle: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'import: {e}")
        return False

if __name__ == "__main__":
    print("Test de configuration ccache pour l'application poker AI")
    print("=" * 50)
    
    ccache_ok = test_ccache()
    paddle_ok = test_paddle_import()
    
    print("\n" + "=" * 50)
    if ccache_ok and paddle_ok:
        print("✅ Configuration complète réussie!")
        print("L'application devrait maintenant fonctionner sans avertissements ccache.")
    else:
        print("❌ Certains tests ont échoué.")
        print("Vérifiez la configuration de ccache.") 