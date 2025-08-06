#!/usr/bin/env python3
"""
Training optimisé basé sur les paramètres qui ont fonctionné
Utilise dataset andy8744 complet avec paramètres proven
"""

import os
import sys
import time
from pathlib import Path
from ultralytics import YOLO

def train_with_proven_params():
    """Training avec paramètres qui ont prouvé leur efficacité."""
    print("=== TRAINING OPTIMISE ANDY8744 ===")
    print("Base sur parametres proven du optimized_train.py")
    
    # Vérifier dataset complet
    config_file = "data_andy8744_ready.yaml"
    if not Path(config_file).exists():
        print(f"ERROR: {config_file} not found!")
        return False
    
    print(f"Dataset: andy8744 complet (20,000 images)")
    print(f"Config: {config_file}")
    
    start_time = time.time()
    
    try:
        # Charger modèle
        model = YOLO('yolov8n.pt')
        print("Model: YOLOv8 Nano")
        
        # Paramètres optimisés (basés sur optimized_train.py)
        train_args = {
            'data': config_file,
            'epochs': 10,           # Comme dans optimized_train
            'batch': 16,            # Comme dans optimized_train  
            'imgsz': 416,           # Comme dans optimized_train
            'device': 'cpu',        # CPU pour compatibilité
            'workers': 4,           # Comme dans optimized_train
            'cache': False,         # False pour éviter RAM overflow
            'amp': False,           # False pour CPU
            'patience': 5,          # Comme dans optimized_train
            'save_period': 2,       # Sauver chaque 2 epochs
            'name': "andy8744_optimized",
            'verbose': True,
            'plots': True,
            'save': True,
            
            # Paramètres d'augmentation (comme optimized_train)
            'mosaic': 1.0,          # Augmentation cruciale
            'mixup': 0.0,
            'hsv_h': 0.015,
            'hsv_s': 0.7, 
            'hsv_v': 0.4,
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'fliplr': 0.5,          # Flip horizontal
            'auto_augment': 'randaugment',
            
            # Learning rate optimisé
            'lr0': 0.01,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3.0,
            'warmup_momentum': 0.8,
        }
        
        print("\n=== PARAMETRES OPTIMISES ===")
        key_params = ['epochs', 'batch', 'imgsz', 'cache', 'mosaic', 'lr0', 'warmup_epochs']
        for param in key_params:
            if param in train_args:
                print(f"  {param}: {train_args[param]}")
        
        print(f"\nStarting optimized training (10 epochs)...")
        print("Cela va prendre 1-2 heures sur CPU...")
        
        # Training
        results = model.train(**train_args)
        
        end_time = time.time()
        training_time = (end_time - start_time) / 60  # minutes
        
        print(f"\n=== TRAINING COMPLETED ===")
        print(f"Duration: {training_time:.1f} minutes")
        print(f"Results: {results.save_dir}")
        
        return True, results.save_dir
        
    except Exception as e:
        print(f"ERROR during training: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def test_trained_model(model_path):
    """Test modèle avec dataset complet."""
    print(f"\n=== TESTING TRAINED MODEL ===")
    
    try:
        model = YOLO(model_path)
        
        # Test sur images andy8744 test
        test_dir = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4/test/images")
        test_images = list(test_dir.glob("*.jpg"))[:10]  # 10 images test
        
        total_detections = 0
        
        for img_path in test_images:
            print(f"Testing: {img_path.name}")
            
            results = model(str(img_path), verbose=False)
            
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    detections = len(boxes)
                    total_detections += detections
                    print(f"  -> {detections} detections")
                    
                    # Montrer meilleures détections
                    for i, box in enumerate(boxes[:3]):  # Top 3
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        cls_name = model.names[cls_id]
                        print(f"     {i+1}. {cls_name} ({conf:.3f})")
                else:
                    print("  -> No detections")
        
        print(f"\n=== INFERENCE RESULTS ===")
        print(f"Total detections: {total_detections}")
        print(f"Average per image: {total_detections/len(test_images):.1f}")
        
        return total_detections > 0
        
    except Exception as e:
        print(f"ERROR during inference: {e}")
        return False

def main():
    print("Training optimisé basé sur les paramètres proven")
    print("Dataset: andy8744 complet (20,000 images)")
    print("Duration estimée: 1-2 heures")
    print("\nContinuer? (y/N): ", end="")
    
    response = input().strip().lower()
    if response != 'y':
        print("Training annulé.")
        return
    
    # Training optimisé
    success, info = train_with_proven_params()
    
    if success:
        print("\n✓ Training optimisé réussi!")
        
        # Test inference
        best_model = Path(info) / "weights" / "best.pt"
        if best_model.exists():
            inference_success = test_trained_model(str(best_model))
            
            print("\n=== FINAL RESULTS ===")
            if inference_success:
                print("SUCCESS: Training ET inference réussis!")
                print("✓ Dataset andy8744: WORKING")
                print("✓ Paramètres optimisés: WORKING")
                print("✓ Model détecte des cartes: WORKING")
                print(f"✓ Best model: {best_model}")
            else:
                print("PARTIAL: Training OK mais inference faible")
        else:
            print("ERROR: Best model non trouvé")
    else:
        print(f"\n✗ Training échoué: {info}")

if __name__ == "__main__":
    main()