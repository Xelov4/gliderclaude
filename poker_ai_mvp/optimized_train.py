#!/usr/bin/env python3
"""
Optimized YOLO Training Script for GTX 1080 Ti
Maximizes GPU and CPU utilization with optimal parameters
"""

import os
import sys
import torch
import argparse
from pathlib import Path
from ultralytics import YOLO
import psutil
import gc

def optimize_system():
    """Optimize system for training"""
    print("🔧 Optimizing system for training...")
    
    # Clear GPU cache
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print(f"✅ GPU cache cleared")
    
    # Clear Python cache
    gc.collect()
    print(f"✅ Python memory cache cleared")
    
    # Set optimal PyTorch settings
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    print(f"✅ PyTorch optimizations applied")

def get_optimal_parameters():
    """Get optimal training parameters for GTX 1080 Ti"""
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
    
    if gpu_memory >= 10:  # GTX 1080 Ti has 11GB
        return {
            'batch_size': 64,      # Large batch size for GPU
            'image_size': 640,     # Standard YOLO size
            'epochs': 10,          # Reasonable for testing
            'workers': 8,          # Multiple CPU workers
            'device': '0',         # Use GPU
            'cache': True,         # Cache images in RAM
            'amp': True,           # Mixed precision training
            'patience': 5,         # Early stopping
            'save_period': 2,      # Save every 2 epochs
        }
    else:
        return {
            'batch_size': 32,
            'image_size': 512,
            'epochs': 5,
            'workers': 4,
            'device': '0',
            'cache': False,
            'amp': True,
            'patience': 3,
            'save_period': 1,
        }

def monitor_resources():
    """Monitor system resources"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    if torch.cuda.is_available():
        gpu_memory_used = torch.cuda.memory_allocated(0) / 1024**3
        gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        print(f"📊 System Monitor:")
        print(f"   CPU Usage: {cpu_percent}%")
        print(f"   RAM Usage: {memory.percent}% ({memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB)")
        print(f"   GPU Memory: {gpu_memory_used:.1f}GB / {gpu_memory_total:.1f}GB")
        print(f"   GPU Device: {torch.cuda.get_device_name(0)}")

def main():
    parser = argparse.ArgumentParser(description="Optimized YOLO Training")
    parser.add_argument("dataset_path", help="Path to dataset directory")
    parser.add_argument("--epochs", type=int, default=None, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument("--image-size", type=int, default=None, help="Image size")
    parser.add_argument("--workers", type=int, default=None, help="Number of workers")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode with minimal epochs")
    
    args = parser.parse_args()
    
    # System optimization
    optimize_system()
    
    # Get optimal parameters
    optimal_params = get_optimal_parameters()
    
    # Override with command line arguments or test mode
    if args.test_mode:
        optimal_params.update({
            'epochs': 2,
            'batch_size': 16,
            'image_size': 416,
            'workers': 4,
        })
    else:
        if args.epochs:
            optimal_params['epochs'] = args.epochs
        if args.batch_size:
            optimal_params['batch_size'] = args.batch_size
        if args.image_size:
            optimal_params['image_size'] = args.image_size
        if args.workers:
            optimal_params['workers'] = args.workers
    
    print(f"🚀 Starting optimized training with parameters:")
    for key, value in optimal_params.items():
        print(f"   {key}: {value}")
    
    # Monitor initial resources
    monitor_resources()
    
    # Initialize model
    model = YOLO('yolov8n.pt')  # Start with nano model for testing
    
    # Training arguments
    train_args = {
        'data': str(Path(args.dataset_path) / 'data.yaml'),
        'epochs': optimal_params['epochs'],
        'batch': optimal_params['batch_size'],
        'imgsz': optimal_params['image_size'],
        'device': optimal_params['device'],
        'workers': optimal_params['workers'],
        'cache': optimal_params['cache'],
        'amp': optimal_params['amp'],
        'patience': optimal_params['patience'],
        'save_period': optimal_params['save_period'],
        'project': 'optimized_training',
        'name': f'cards_yolo_optimized_{optimal_params["epochs"]}ep',
        'verbose': True,
        'plots': True,
        'save': True,
    }
    
    print(f"\n🎯 Training Configuration:")
    for key, value in train_args.items():
        print(f"   {key}: {value}")
    
    try:
        # Start training
        print(f"\n🔥 Starting training...")
        results = model.train(**train_args)
        
        print(f"\n✅ Training completed successfully!")
        print(f"📁 Results saved to: {results.save_dir}")
        
        # Final resource check
        monitor_resources()
        
        return results
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None

if __name__ == "__main__":
    main() 