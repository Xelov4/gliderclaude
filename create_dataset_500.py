#!/usr/bin/env python3
"""
Créer mini-dataset de 500 images pour test GPU optimisé
Distribution: 300 train, 100 valid, 100 test
"""

import os
import shutil
import sys
from pathlib import Path
import yaml

def create_dataset_500():
    """Créer dataset de 500 images exactement."""
    print("=== CREATION DATASET 500 IMAGES POUR TEST GPU ===")
    
    # Paths
    original_dataset = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4")
    gpu_dataset = Path("data/gpu_test_500")
    
    # Nettoyer si existe
    if gpu_dataset.exists():
        print("Cleaning existing dataset...")
        shutil.rmtree(gpu_dataset)
    
    # Créer structure
    for split in ["train", "valid", "test"]:
        (gpu_dataset / split / "images").mkdir(parents=True, exist_ok=True)
        (gpu_dataset / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Distribution optimisée pour training: 300 train, 100 val, 100 test
    split_counts = {"train": 300, "valid": 100, "test": 100}
    
    total_copied = 0
    
    for split, target_count in split_counts.items():
        src_images = original_dataset / split / "images"
        src_labels = original_dataset / split / "labels"
        
        print(f"Processing {split} ({target_count} images)...")
        
        # Prendre images qui ont des labels
        image_files = list(src_images.glob("*.jpg"))
        copied_count = 0
        
        for img_file in image_files:
            if copied_count >= target_count:
                break
            
            # Chercher label correspondant
            label_file = src_labels / (img_file.stem + ".txt")
            
            if label_file.exists():
                # Copier image ET label
                shutil.copy2(img_file, gpu_dataset / split / "images")
                shutil.copy2(label_file, gpu_dataset / split / "labels")
                copied_count += 1
                total_copied += 1
        
        print(f"  -> {copied_count}/{target_count} images copiées")
    
    # Créer data.yaml avec dataset andy8744 (52 classes)
    gpu_yaml = {
        "train": str((gpu_dataset / "train" / "images").resolve()),
        "val": str((gpu_dataset / "valid" / "images").resolve()),
        "test": str((gpu_dataset / "test" / "images").resolve()),
        "nc": 52,  # 52 classes comme andy8744
        "names": ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    }
    
    yaml_file = "data_gpu_test_500.yaml"
    with open(yaml_file, 'w') as f:
        yaml.dump(gpu_yaml, f, default_flow_style=False)
    
    print(f"\n=== DATASET GPU 500 READY ===")
    print(f"Total images: {total_copied}")
    print(f"Distribution: 300 train, 100 valid, 100 test")
    print(f"Classes: 52 (andy8744 format)")
    print(f"Dataset path: {gpu_dataset}")
    print(f"Config file: {yaml_file}")
    
    # Vérifier distribution des classes dans les labels
    print(f"\nVérification des labels...")
    for split in ["train", "valid", "test"]:
        label_dir = gpu_dataset / split / "labels"
        labels = list(label_dir.glob("*.txt"))
        
        classes_found = set()
        total_annotations = 0
        
        for label_file in labels:
            with open(label_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if parts:
                        cls_id = int(parts[0])
                        classes_found.add(cls_id)
                        total_annotations += 1
        
        print(f"  {split}: {len(labels)} labels, {total_annotations} annotations, {len(classes_found)} classes uniques")
    
    return yaml_file

def main():
    config_file = create_dataset_500()
    print(f"\nDataset ready for GPU training test: {config_file}")
    return config_file

if __name__ == "__main__":
    main()