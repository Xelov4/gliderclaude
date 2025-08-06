#!/usr/bin/env python3
"""
Créer mini-dataset pour training test rapide
200 images max (100 train, 50 valid, 50 test)
"""

import os
import shutil
import sys
from pathlib import Path
import yaml

def create_mini_dataset_200():
    """Créer mini-dataset de 200 images exactement."""
    print("=== CREATION MINI-DATASET 200 IMAGES ===")
    
    # Paths
    original_dataset = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4")
    mini_dataset = Path("data/mini_andy_200")
    
    # Nettoyer si existe
    if mini_dataset.exists():
        print("Cleaning existing mini dataset...")
        shutil.rmtree(mini_dataset)
    
    # Créer structure
    for split in ["train", "valid", "test"]:
        (mini_dataset / split / "images").mkdir(parents=True, exist_ok=True)
        (mini_dataset / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Distribution: 100 train, 50 valid, 50 test = 200 total
    split_counts = {"train": 100, "valid": 50, "test": 50}
    
    total_copied = 0
    
    for split, target_count in split_counts.items():
        src_images = original_dataset / split / "images"
        src_labels = original_dataset / split / "labels"
        
        print(f"Processing {split}...")
        
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
                shutil.copy2(img_file, mini_dataset / split / "images")
                shutil.copy2(label_file, mini_dataset / split / "labels")
                copied_count += 1
                total_copied += 1
        
        print(f"  -> {copied_count}/{target_count} images copiées")
    
    # Créer data.yaml pour mini-dataset
    mini_yaml = {
        "train": str((mini_dataset / "train" / "images").resolve()),
        "val": str((mini_dataset / "valid" / "images").resolve()),
        "test": str((mini_dataset / "test" / "images").resolve()),
        "nc": 52,
        "names": ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']
    }
    
    yaml_file = "data_mini_andy_200.yaml"
    with open(yaml_file, 'w') as f:
        yaml.dump(mini_yaml, f, default_flow_style=False)
    
    print(f"\n=== MINI-DATASET READY ===")
    print(f"Total images: {total_copied}")
    print(f"Dataset path: {mini_dataset}")
    print(f"Config file: {yaml_file}")
    
    return yaml_file

def main():
    config_file = create_mini_dataset_200()
    print(f"\nReady for training with: {config_file}")
    return config_file

if __name__ == "__main__":
    main()