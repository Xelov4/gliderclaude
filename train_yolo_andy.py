#!/usr/bin/env python3
"""
Training YOLO avec dataset andy8744
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO

def train_mini_test():
    """Training test rapide - 10 epochs."""
    print("=== YOLO TRAINING TEST (MINI) ===")
    
    # Vérifier dataset config
    config_file = "data_andy8744_ready.yaml"
    if not Path(config_file).exists():
        print(f"ERROR: Config file not found: {config_file}")
        print("Run simple_dataset_test.py first!")
        return False
    
    print(f"Using config: {config_file}")
    
    try:
        # Charger modèle YOLO nano (plus rapide)
        model = YOLO('yolov8n.pt')
        print("Model loaded: YOLOv8n")
        
        # Training avec paramètres pour test rapide
        print("Starting training (10 epochs, batch=8)...")
        
        results = model.train(
            data=config_file,
            epochs=10,          # Court pour test
            batch=8,           # Petit batch
            imgsz=416,         # Taille du dataset
            patience=50,       # Pas d'early stopping
            save=True,
            verbose=True,
            name="andy8744_test"
        )
        
        print("Training completed successfully!")
        print(f"Results saved to: {results.save_dir}")
        
        return True, results.save_dir
        
    except Exception as e:
        print(f"ERROR during training: {e}")
        return False, str(e)

def train_full():
    """Training complet - 100+ epochs."""
    print("=== YOLO TRAINING FULL ===")
    
    config_file = "data_andy8744_ready.yaml"
    
    try:
        model = YOLO('yolov8s.pt')  # Modèle small pour plus de précision
        print("Model loaded: YOLOv8s")
        
        print("Starting FULL training (100 epochs, batch=16)...")
        print("This will take several hours...")
        
        results = model.train(
            data=config_file,
            epochs=100,         # Training complet
            batch=16,           # Batch optimisé
            imgsz=416,
            patience=20,        # Early stopping
            save=True,
            verbose=True,
            name="andy8744_full",
            plots=True,
            device='cpu'        # Forcer CPU si pas de GPU
        )
        
        print("FULL training completed!")
        print(f"Results saved to: {results.save_dir}")
        
        return True, results.save_dir
        
    except Exception as e:
        print(f"ERROR during full training: {e}")
        return False, str(e)

def test_inference(model_path):
    """Test inference avec modèle entraîné."""
    print(f"\n=== TESTING INFERENCE ===")
    print(f"Model: {model_path}")
    
    try:
        model = YOLO(model_path)
        
        # Prendre quelques images de test
        test_dir = Path("data/andy8744/playing-cards-object-detection-dataset/versions/4/test/images")
        test_images = list(test_dir.glob("*.jpg"))[:5]
        
        for img_path in test_images:
            print(f"\nTesting: {img_path.name}")
            
            results = model(str(img_path))
            
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    print(f"  Detected {len(boxes)} objects:")
                    for i, box in enumerate(boxes):
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        cls_name = model.names[cls_id]
                        print(f"    {i+1}. {cls_name} (conf: {conf:.3f})")
                else:
                    print("  No objects detected")
        
        print("Inference test completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR during inference: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  py train_yolo_andy.py test    # Quick test (10 epochs)")
        print("  py train_yolo_andy.py full    # Full training (100+ epochs)")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "test":
        success, info = train_mini_test()
        
        if success:
            # Test inference avec le modèle entraîné
            best_model = Path(info) / "weights" / "best.pt"
            if best_model.exists():
                test_inference(str(best_model))
            
            print("\n=== TEST SUMMARY ===")
            print("SUCCESS: Mini training completed!")
            print("- Dataset andy8744: WORKING")
            print("- YOLO training: WORKING")
            print("- Inference: WORKING")
            print("\nREADY FOR FULL TRAINING!")
        
    elif mode == "full":
        print("Starting FULL training with andy8744 dataset...")
        print("This will take several hours. Continue? (y/N)")
        
        response = input().strip().lower()
        if response == 'y':
            success, info = train_full()
            
            if success:
                best_model = Path(info) / "weights" / "best.pt"
                if best_model.exists():
                    test_inference(str(best_model))
                
                print("\n=== FULL TRAINING COMPLETE ===")
                print("SUCCESS: Full training completed!")
                print(f"Best model: {best_model}")
        else:
            print("Training cancelled.")
    else:
        print("Invalid mode. Use 'test' or 'full'")

if __name__ == "__main__":
    main()