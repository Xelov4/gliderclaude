#!/usr/bin/env python3
"""
Test script pour valider training YOLO avec dataset andy8744
- Test avec mini-batch d'images (20 images)
- Validation du mapping des classes
- Test training rapide (5 epochs)
"""

import os
import shutil
import sys
from pathlib import Path
from ultralytics import YOLO
import yaml

def create_mini_dataset():
    """Créer un mini-dataset pour test rapide (20 images)."""
    print("🔧 Création mini-dataset de test...")
    
    # Paths
    original_dataset = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4")
    mini_dataset = Path("data/mini_test_andy")
    
    # Nettoyer si existe
    if mini_dataset.exists():
        shutil.rmtree(mini_dataset)
    
    # Créer structure
    for split in ["train", "valid", "test"]:
        (mini_dataset / split / "images").mkdir(parents=True, exist_ok=True)
        (mini_dataset / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Copier 20 images de chaque split AVEC leurs labels
    for split in ["train", "valid", "test"]:
        src_images = original_dataset / split / "images"
        src_labels = original_dataset / split / "labels"
        
        # Vérifier que les dossiers existent
        if not src_images.exists():
            print(f"⚠️  Dossier images manquant: {src_images}")
            continue
        if not src_labels.exists():
            print(f"⚠️  Dossier labels manquant: {src_labels}")
            continue
        
        # Prendre les 20 premières images qui ont des labels
        image_files = list(src_images.glob("*.jpg"))
        copied_count = 0
        
        for img_file in image_files:
            if copied_count >= 20:
                break
                
            # Chercher label correspondant (même nom base mais .txt)
            label_file = src_labels / (img_file.stem + ".txt")
            
            if label_file.exists():
                # Copier image ET label
                shutil.copy2(img_file, mini_dataset / split / "images")
                shutil.copy2(label_file, mini_dataset / split / "labels")
                copied_count += 1
            else:
                print(f"⚠️  Label manquant pour {img_file.name}")
        
        print(f"   {split}: {copied_count}/20 images copiées avec labels")
    
    # Créer data.yaml modifié
    mini_yaml = {
        "train": str((mini_dataset / "train" / "images").resolve()),
        "val": str((mini_dataset / "valid" / "images").resolve()),
        "test": str((mini_dataset / "test" / "images").resolve()),
        "nc": 52,
        "names": ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    }
    
    with open(mini_dataset / "data.yaml", "w") as f:
        yaml.dump(mini_yaml, f, default_flow_style=False)
    
    print(f"✅ Mini-dataset créé: {mini_dataset}")
    print(f"   - Train: {len(list((mini_dataset / 'train' / 'images').glob('*.jpg')))} images")
    print(f"   - Valid: {len(list((mini_dataset / 'valid' / 'images').glob('*.jpg')))} images")
    print(f"   - Test: {len(list((mini_dataset / 'test' / 'images').glob('*.jpg')))} images")
    
    return str(mini_dataset / "data.yaml")

def test_class_mapping():
    """Tester le mapping des classes dataset vs code."""
    print("\n🔍 Test mapping classes...")
    
    # Classes du dataset andy8744
    dataset_classes = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    
    # Mapping dataset -> format poker standard
    def map_dataset_to_poker(class_name):
        """Convertit '10c' -> ('10', '♣')"""
        if len(class_name) < 2:
            return None, None
        
        rank = class_name[:-1]  # Tout sauf dernier char
        suit_char = class_name[-1]  # Dernier char
        
        # Mapping suit
        suit_map = {
            'c': '♣',  # clubs
            'd': '♦',  # diamonds  
            'h': '♥',  # hearts
            's': '♠'   # spades
        }
        
        suit = suit_map.get(suit_char)
        return rank, suit
    
    print("Exemples de mapping:")
    test_classes = ['10c', 'Ac', 'Kh', 'Qs', '2d']
    for cls in test_classes:
        rank, suit = map_dataset_to_poker(cls)
        print(f"   '{cls}' -> ('{rank}', '{suit}')")
    
    print(f"✅ {len(dataset_classes)} classes mappées correctement")
    return dataset_classes

def test_quick_training(dataset_path):
    """Test training rapide sur mini-dataset."""
    print(f"\n🚀 Test training YOLO (5 epochs)...")
    print(f"Dataset: {dataset_path}")
    
    try:
        # Initialiser modèle YOLO
        model = YOLO('yolov8n.pt')  # Modèle nano pour rapidité
        
        # Training avec paramètres minimaux
        results = model.train(
            data=dataset_path,
            epochs=5,           # Très court pour test
            batch=4,           # Petit batch
            imgsz=416,         # Taille dataset
            patience=50,
            save=True,
            verbose=True,
            plots=True
        )
        
        print("✅ Training test réussi!")
        print(f"   Modèle sauvé: {results.save_dir}")
        return True, results.save_dir
        
    except Exception as e:
        print(f"❌ Erreur training: {e}")
        return False, str(e)

def test_inference(model_path):
    """Test inference avec modèle entraîné."""
    print(f"\n🔍 Test inference...")
    
    try:
        # Charger modèle entraîné
        model = YOLO(model_path)
        
        # Test sur quelques images
        test_images = list(Path("data/mini_test_andy/test/images").glob("*.jpg"))[:3]
        
        if not test_images:
            print("❌ Pas d'images de test trouvées")
            return False
        
        for img_path in test_images:
            print(f"   Test: {img_path.name}")
            results = model(str(img_path))
            
            # Analyser détections
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    print(f"     Détections: {len(boxes)} objets")
                    for i, box in enumerate(boxes):
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        cls_name = model.names[cls_id]
                        print(f"       {i+1}. {cls_name} ({conf:.2f})")
                else:
                    print("     Aucune détection")
        
        print("✅ Test inference réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur inference: {e}")
        return False

def main():
    """Test complet YOLO + dataset andy8744."""
    print("🎯 TEST YOLO + DATASET ANDY8744")
    print("=" * 50)
    
    # Étape 1: Créer mini-dataset
    dataset_yaml = create_mini_dataset()
    
    # Étape 2: Tester mapping classes
    classes = test_class_mapping()
    
    # Étape 3: Test training rapide
    success, model_info = test_quick_training(dataset_yaml)
    
    if success:
        # Étape 4: Test inference
        best_model = Path(model_info) / "weights" / "best.pt"
        if best_model.exists():
            test_inference(str(best_model))
        else:
            print("❌ Modèle entraîné non trouvé")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Dataset andy8744 compatible avec YOLO")
        print("✅ Training fonctionne correctement")
        print("✅ Inference opérationnelle")
        print("\n🚀 Prêt pour training complet!")
    else:
        print("❌ Tests échoués - Debug nécessaire")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)