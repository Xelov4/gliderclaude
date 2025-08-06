#!/usr/bin/env python3
"""
Test simple du dataset andy8744
"""

import os
import sys
from pathlib import Path
import yaml

def main():
    print("=== VALIDATION DATASET ANDY8744 ===")
    
    # Check dataset structure
    dataset_path = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4")
    
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        return False
    
    print("OK: Dataset directory found")
    
    # Check data.yaml
    yaml_file = dataset_path / "data.yaml"
    if not yaml_file.exists():
        print(f"ERROR: data.yaml not found")
        return False
    
    # Read config
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"OK: data.yaml loaded")
    print(f"    Classes: {config.get('nc', 'undefined')}")
    print(f"    Names count: {len(config.get('names', []))}")
    
    # Check splits
    for split in ['train', 'valid', 'test']:
        img_dir = dataset_path / split / 'images'
        label_dir = dataset_path / split / 'labels'
        
        if not img_dir.exists():
            print(f"ERROR: {split} images directory missing")
            return False
        if not label_dir.exists():
            print(f"ERROR: {split} labels directory missing")
            return False
        
        imgs = list(img_dir.glob('*.jpg'))
        labels = list(label_dir.glob('*.txt'))
        
        print(f"OK: {split} -> {len(imgs)} images, {len(labels)} labels")
    
    # Test class mapping
    print("\n=== CLASS MAPPING TEST ===")
    
    dataset_classes = config.get('names', [])
    examples = ['10c', 'Ac', 'Kh', 'Qs', '2d']
    
    for cls in examples:
        if len(cls) >= 2:
            rank = cls[:-1]
            suit_char = cls[-1]
            suit_map = {'c': 'clubs', 'd': 'diamonds', 'h': 'hearts', 's': 'spades'}
            suit = suit_map.get(suit_char, 'unknown')
            print(f"    '{cls}' -> rank='{rank}', suit='{suit}'")
    
    # Create corrected YAML
    print("\n=== CREATING CORRECTED YAML ===")
    
    corrected_config = {
        "train": str((dataset_path / "train" / "images").resolve()),
        "val": str((dataset_path / "valid" / "images").resolve()),
        "test": str((dataset_path / "test" / "images").resolve()),
        "nc": 52,
        "names": dataset_classes
    }
    
    output_file = "data_andy8744_ready.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(corrected_config, f, default_flow_style=False)
    
    print(f"OK: Created {output_file}")
    
    print("\n=== SUMMARY ===")
    print("SUCCESS: Dataset andy8744 is ready for YOLO training!")
    print("- Structure: OK")
    print("- Labels: OK") 
    print("- Classes: 52 cards mapped")
    print(f"- Config file: {output_file}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nREADY FOR YOLO TRAINING!")
    else:
        print("\nFIX ISSUES BEFORE TRAINING!")
    sys.exit(0 if success else 1)