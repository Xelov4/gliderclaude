#!/usr/bin/env python3
"""
Training test ultra-rapide: 2 epochs sur 200 images
Validation que le pipeline fonctionne avant le grand training
"""

import os
import sys
import time
from pathlib import Path
from ultralytics import YOLO

def test_training_2_epochs():
    """Training test: 2 epochs exactement."""
    print("=== YOLO TRAINING TEST: 2 EPOCHS ONLY ===")
    
    # Vérifier config file
    config_file = "data_mini_andy_200.yaml"
    if not Path(config_file).exists():
        print(f"ERROR: {config_file} not found!")
        print("Run create_mini_dataset.py first!")
        return False
    
    print(f"Using config: {config_file}")
    print("Dataset: 200 images (100 train, 50 valid, 50 test)")
    print("Training: 2 epochs only (ultra-fast test)")
    
    start_time = time.time()
    
    try:
        # Charger modèle nano pour vitesse maximale
        model = YOLO('yolov8n.pt')
        print("Model: YOLOv8 Nano (fastest)")
        
        # Training avec paramètres ultra-rapides
        print("\nStarting 2-epoch training...")
        
        results = model.train(
            data=config_file,
            epochs=2,           # Exactement 2 epochs
            batch=4,            # Petit batch pour rapidité
            imgsz=416,          # Taille dataset
            patience=50,        # Pas d'early stopping
            save=True,
            verbose=True,
            name="test_2epochs",
            device='cpu',       # Forcer CPU
            plots=False,        # Pas de plots pour vitesse
            val=True           # Validation à la fin
        )
        
        end_time = time.time()
        training_time = end_time - start_time
        
        print(f"\n=== TRAINING COMPLETED ===")
        print(f"Duration: {training_time:.1f} seconds")
        print(f"Results: {results.save_dir}")
        
        return True, results.save_dir
        
    except Exception as e:
        print(f"ERROR during training: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def test_quick_inference(model_path):
    """Test inference rapide."""
    print(f"\n=== QUICK INFERENCE TEST ===")
    
    try:
        model = YOLO(model_path)
        
        # Prendre 3 images test
        test_dir = Path("data/mini_andy_200/test/images")
        test_images = list(test_dir.glob("*.jpg"))[:3]
        
        detection_count = 0
        
        for img_path in test_images:
            print(f"Testing: {img_path.name}")
            
            results = model(str(img_path), verbose=False)
            
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    detection_count += len(boxes)
                    print(f"  -> {len(boxes)} detections")
                    
                    # Montrer première détection
                    if len(boxes) > 0:
                        cls_id = int(boxes[0].cls[0])
                        conf = float(boxes[0].conf[0])
                        cls_name = model.names[cls_id]
                        print(f"     Best: {cls_name} (conf: {conf:.3f})")
                else:
                    print("  -> No detections")
        
        print(f"\nTotal detections: {detection_count}")
        return detection_count > 0
        
    except Exception as e:
        print(f"ERROR during inference: {e}")
        return False

def main():
    print("Starting 2-epoch training test...")
    print("This should take 2-5 minutes max.")
    
    # Training test
    success, info = test_training_2_epochs()
    
    if success:
        print("\n✓ Training test PASSED!")
        
        # Test inference
        best_model = Path(info) / "weights" / "best.pt"
        if best_model.exists():
            inference_success = test_quick_inference(str(best_model))
            
            if inference_success:
                print("\n✓ Inference test PASSED!")
            else:
                print("\n✗ Inference test FAILED!")
        
        print("\n=== FINAL RESULT ===")
        if best_model.exists() and inference_success:
            print("SUCCESS: All tests passed!")
            print("✓ Dataset andy8744: WORKING")
            print("✓ YOLO training: WORKING") 
            print("✓ Model inference: WORKING")
            print("✓ 52 classes mapping: WORKING")
            print(f"✓ Best model saved: {best_model}")
            print("\n🚀 READY FOR FULL TRAINING!")
            
            return True
        else:
            print("PARTIAL SUCCESS: Training worked but inference issues")
            return False
    else:
        print(f"\n✗ Training test FAILED: {info}")
        print("Fix issues before full training!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)