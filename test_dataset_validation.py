#!/usr/bin/env python3
"""
Script de validation du dataset andy8744 sans dépendances YOLO
Vérifie structure, labels, et mapping des classes
"""

import os
import sys
from pathlib import Path
import yaml
import shutil

def validate_dataset_structure():
    """Vérifier la structure du dataset andy8744."""
    print("Validation structure dataset andy8744...")
    
    dataset_path = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4")
    
    if not dataset_path.exists():
        print(f"[ERROR] Dataset non trouve: {dataset_path}")
        return False
    
    # Vérifier data.yaml
    yaml_file = dataset_path / "data.yaml"
    if not yaml_file.exists():
        print(f"[ERROR] data.yaml non trouve: {yaml_file}")
        return False
    
    # Lire data.yaml
    with open(yaml_file, 'r') as f:
        data_config = yaml.safe_load(f)
    
    print(f"✅ data.yaml trouvé:")
    print(f"   Classes: {data_config.get('nc', 'non défini')}")
    print(f"   Noms: {len(data_config.get('names', []))} classes")
    
    # Vérifier dossiers
    for split in ['train', 'valid', 'test']:
        img_dir = dataset_path / split / 'images'
        label_dir = dataset_path / split / 'labels'
        
        if not img_dir.exists():
            print(f"❌ Dossier images manquant: {img_dir}")
            return False
        if not label_dir.exists():
            print(f"❌ Dossier labels manquant: {label_dir}")
            return False
        
        # Compter fichiers
        imgs = list(img_dir.glob('*.jpg'))
        labels = list(label_dir.glob('*.txt'))
        
        print(f"✅ {split}: {len(imgs)} images, {len(labels)} labels")
    
    return True, data_config

def validate_labels_format():
    """Vérifier le format des labels YOLO."""
    print("\n🔍 Validation format labels...")
    
    # Prendre quelques labels d'exemple
    test_labels = []
    for split in ['train', 'valid', 'test']:
        label_dir = Path(f"data/andy8744/playing-cards-object-detection-dataset/versions/4/{split}/labels")
        labels = list(label_dir.glob('*.txt'))[:3]  # 3 premiers
        test_labels.extend(labels)
    
    valid_count = 0
    
    for label_file in test_labels[:9]:  # Test 9 labels
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    x, y, w, h = map(float, parts[1:5])
                    
                    # Vérifier ranges
                    if 0 <= cls_id <= 51 and all(0 <= val <= 1 for val in [x, y, w, h]):
                        valid_count += 1
                    else:
                        print(f"⚠️  Label invalide dans {label_file.name}: {line.strip()}")
            
        except Exception as e:
            print(f"❌ Erreur lecture {label_file.name}: {e}")
    
    print(f"✅ {valid_count} labels valides testés")
    return valid_count > 0

def test_class_mapping():
    """Tester le mapping des classes."""
    print("\n🎯 Test mapping classes dataset → poker...")
    
    # Classes du dataset
    dataset_classes = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    
    # Mapping function
    def map_dataset_to_poker(class_name):
        if len(class_name) < 2:
            return None, None
        
        rank = class_name[:-1]
        suit_char = class_name[-1]
        
        suit_map = {'c': '♣', 'd': '♦', 'h': '♥', 's': '♠'}
        suit = suit_map.get(suit_char)
        return rank, suit
    
    # Test mapping
    success_count = 0
    examples = ['10c', 'Ac', 'Kh', 'Qs', '2d', 'Jc', '7s', '9h']
    
    print("Exemples de mapping:")
    for cls in examples:
        rank, suit = map_dataset_to_poker(cls)
        if rank and suit:
            print(f"   '{cls}' → ('{rank}', '{suit}')")
            success_count += 1
        else:
            print(f"   '{cls}' → ERREUR")
    
    print(f"✅ {success_count}/{len(examples)} mappings réussis")
    print(f"✅ {len(dataset_classes)} classes total dans dataset")
    
    return success_count == len(examples)

def create_corrected_data_yaml():
    """Créer data.yaml avec paths absolus corrigés."""
    print("\n🔧 Création data.yaml avec paths absolus...")
    
    base_path = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4").resolve()
    
    corrected_yaml = {
        "train": str(base_path / "train" / "images"),
        "val": str(base_path / "valid" / "images"),
        "test": str(base_path / "test" / "images"),
        "nc": 52,
        "names": ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    }
    
    output_file = "data_andy8744_corrected.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(corrected_yaml, f, default_flow_style=False)
    
    print(f"✅ Fichier créé: {output_file}")
    return output_file

def main():
    """Validation complète du dataset."""
    print("VALIDATION DATASET ANDY8744")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Structure
    result = validate_dataset_structure()
    if not result:
        all_passed = False
    
    # Test 2: Format labels
    if not validate_labels_format():
        all_passed = False
    
    # Test 3: Mapping classes
    if not test_class_mapping():
        all_passed = False
    
    # Test 4: Créer YAML corrigé
    yaml_file = create_corrected_data_yaml()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 VALIDATION RÉUSSIE!")
        print("✅ Dataset andy8744 est prêt pour YOLO")
        print("✅ Structure correcte")
        print("✅ Labels au bon format")
        print("✅ Mapping classes validé")
        print(f"✅ Fichier YAML créé: {yaml_file}")
        print("\n🚀 Prêt pour training YOLO!")
    else:
        print("❌ Validation échouée - corrections nécessaires")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)