#!/usr/bin/env python3
"""
Training test GPU optimisé - 1 epoch sur 500 images
Basé sur les paramètres proven qui ont marché avec le GPU
"""

import os
import sys
import time
import torch
import psutil
import gc
from pathlib import Path
from ultralytics import YOLO

def check_system_resources():
    """Vérifier ressources système disponibles."""
    print("=== SYSTEM RESOURCES CHECK ===")
    
    # CPU
    cpu_count = psutil.cpu_count()
    memory = psutil.virtual_memory()
    print(f"CPU: {cpu_count} cores")
    print(f"RAM: {memory.total/1024**3:.1f}GB total, {memory.available/1024**3:.1f}GB available")
    
    # GPU
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        for i in range(gpu_count):
            gpu_props = torch.cuda.get_device_properties(i)
            gpu_memory = gpu_props.total_memory / 1024**3
            print(f"GPU {i}: {gpu_props.name}, {gpu_memory:.1f}GB VRAM")
        return True, gpu_count
    else:
        print("GPU: Not available (CUDA not detected)")
        return False, 0

def optimize_system_for_gpu():
    """Optimiser système pour training GPU."""
    print("\n=== SYSTEM OPTIMIZATION ===")
    
    # Clear caches
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("✓ GPU cache cleared")
    
    gc.collect()
    print("✓ Python memory cleared")
    
    # Optimizations PyTorch
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    print("✓ PyTorch CUDA optimizations enabled")

def get_optimal_gpu_params(gpu_available=True):
    """Paramètres optimisés basés sur le script proven."""
    if gpu_available:
        # Paramètres basés sur optimized_train.py qui a fonctionné
        return {
            'batch_size': 32,       # Plus gros batch pour GPU
            'image_size': 416,      # Comme dans optimized_train
            'device': '0',          # GPU
            'workers': 8,           # Multi-threading optimisé
            'cache': True,          # Cache images en RAM
            'amp': True,            # Mixed precision pour GPU
            'patience': 10,         # Pas d'early stopping sur 1 epoch
            'save_period': 1,       # Sauver à chaque epoch
        }
    else:
        # Fallback CPU avec paramètres proven
        return {
            'batch_size': 16,       # Réduit pour CPU
            'image_size': 416,
            'device': 'cpu',
            'workers': 4,
            'cache': False,         # Éviter surcharge RAM
            'amp': False,           # AMP pas supporté CPU
            'patience': 10,
            'save_period': 1,
        }

def gpu_training_test():
    """Training test 1 epoch avec config GPU proven."""
    print("=== GPU TRAINING TEST - 1 EPOCH ===")
    
    # Check resources
    gpu_available, gpu_count = check_system_resources()
    
    # System optimization
    optimize_system_for_gpu()
    
    # Vérifier dataset
    config_file = "data_gpu_test_500.yaml"
    if not Path(config_file).exists():
        print(f"ERROR: {config_file} not found!")
        return False
    
    print(f"\nDataset: 500 images (300 train, 100 val, 100 test)")
    print(f"Classes: 52 (andy8744 format)")
    print(f"Config: {config_file}")
    
    # Get optimal parameters
    params = get_optimal_gpu_params(gpu_available)
    
    print(f"\n=== TRAINING PARAMETERS (PROVEN CONFIG) ===")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    start_time = time.time()
    
    try:
        # Load model
        model = YOLO('yolov8n.pt')
        print(f"\nModel: YOLOv8 Nano loaded")
        
        # Training arguments (basés sur optimized_train.py proven)
        train_args = {
            'data': config_file,
            'epochs': 1,                    # 1 epoch seulement pour test
            'batch': params['batch_size'],
            'imgsz': params['image_size'],
            'device': params['device'],
            'workers': params['workers'],
            'cache': params['cache'],
            'amp': params['amp'],
            'patience': params['patience'],
            'save_period': params['save_period'],
            'name': "gpu_test_1epoch",
            'verbose': True,
            'plots': True,
            'save': True,
            
            # Augmentations proven (du optimized_train.py)
            'mosaic': 1.0,              # Crucial pour apprentissage
            'mixup': 0.0,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'fliplr': 0.5,
            'auto_augment': 'randaugment',
            
            # Learning rate proven
            'lr0': 0.01,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 0.0,       # Pas de warmup sur 1 epoch
            'warmup_momentum': 0.8,
            
            # Loss weights proven
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
        }
        
        print(f"\n=== STARTING 1-EPOCH TRAINING ===")
        device_str = "GPU" if gpu_available else "CPU"
        print(f"Device: {device_str}")
        print(f"Estimated time: {'2-5 min' if gpu_available else '10-20 min'}")
        
        # Training
        results = model.train(**train_args)
        
        end_time = time.time()
        training_time = end_time - start_time
        
        print(f"\n=== TRAINING COMPLETED ===")
        print(f"Duration: {training_time:.1f} seconds ({training_time/60:.1f} minutes)")
        print(f"Results: {results.save_dir}")
        
        return True, results.save_dir
        
    except Exception as e:
        print(f"ERROR during training: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def test_inference_advanced(model_path):
    """Test inference avec analyse détaillée."""
    print(f"\n=== ADVANCED INFERENCE TEST ===")
    
    try:
        model = YOLO(model_path)
        
        # Test sur images variées
        test_dir = Path("data/gpu_test_500/test/images")
        test_images = list(test_dir.glob("*.jpg"))[:15]  # 15 images test
        
        total_detections = 0
        confidence_scores = []
        detected_classes = set()
        
        for i, img_path in enumerate(test_images):
            print(f"Testing {i+1}/15: {img_path.name}")
            
            results = model(str(img_path), verbose=False, conf=0.1)  # Seuil bas pour test
            
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    detections = len(boxes)
                    total_detections += detections
                    
                    print(f"  -> {detections} detections")
                    
                    # Analyser détections
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        cls_name = model.names[cls_id]
                        confidence_scores.append(conf)
                        detected_classes.add(cls_name)
                        
                        if conf > 0.3:  # Seulement bonnes détections
                            print(f"     {cls_name}: {conf:.3f}")
                else:
                    print("  -> No detections")
        
        # Analyse des résultats
        print(f"\n=== INFERENCE ANALYSIS ===")
        print(f"Total detections: {total_detections}")
        print(f"Average per image: {total_detections/len(test_images):.1f}")
        print(f"Classes detected: {len(detected_classes)}/52")
        
        if confidence_scores:
            avg_conf = sum(confidence_scores) / len(confidence_scores)
            max_conf = max(confidence_scores)
            print(f"Confidence: avg={avg_conf:.3f}, max={max_conf:.3f}")
            
            # Classes détectées
            print(f"Detected classes: {sorted(list(detected_classes))}")
        
        success = total_detections > 0 and len(detected_classes) > 0
        return success, total_detections, len(detected_classes)
        
    except Exception as e:
        print(f"ERROR during inference: {e}")
        return False, 0, 0

def main():
    print("=== GPU TRAINING TEST - 1 EPOCH / 500 IMAGES ===")
    print("Basé sur paramètres proven du optimized_train.py")
    print("Dataset: andy8744 format (52 classes)")
    
    # Training test
    success, info = gpu_training_test()
    
    if success:
        print("\n✓ Training GPU test PASSED!")
        
        # Test inference avancé
        best_model = Path(info) / "weights" / "best.pt"
        if best_model.exists():
            inference_success, detections, classes = test_inference_advanced(str(best_model))
            
            print("\n=== FINAL RESULTS ===")
            if inference_success and detections > 5:
                print("SUCCESS: Training ET inference fonctionnent!")
                print(f"✓ Dataset andy8744 (52 classes): WORKING")
                print(f"✓ GPU training (1 epoch): WORKING")
                print(f"✓ Model détections: {detections} total")
                print(f"✓ Classes apprises: {classes}/52")
                print(f"✓ Model path: {best_model}")
                print("\n🚀 READY FOR FULL TRAINING!")
                return True
            else:
                print("PARTIAL SUCCESS: Training OK, inference limitée")
                print(f"Détections: {detections} (besoin plus d'epochs)")
                return False
        else:
            print("ERROR: Model non sauvé")
            return False
    else:
        print(f"\n✗ Training failed: {info}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)