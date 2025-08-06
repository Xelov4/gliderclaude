#!/usr/bin/env python3
"""
YOLO Model Training System for Playing Cards
Supports various dataset formats and provides comprehensive training pipeline.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml
import cv2
import numpy as np
from datetime import datetime

try:
    from ultralytics import YOLO
    import torch
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("ERROR: Ultralytics not available. Install with: pip install ultralytics")

# Playing card classes (standard 52-card deck)
CARD_CLASSES = {
    # Spades
    'AS': 0, '2S': 1, '3S': 2, '4S': 3, '5S': 4, '6S': 5, '7S': 6, '8S': 7, '9S': 8, '10S': 9, 'JS': 10, 'QS': 11, 'KS': 12,
    # Hearts  
    'AH': 13, '2H': 14, '3H': 15, '4H': 16, '5H': 17, '6H': 18, '7H': 19, '8H': 20, '9H': 21, '10H': 22, 'JH': 23, 'QH': 24, 'KH': 25,
    # Diamonds
    'AD': 26, '2D': 27, '3D': 28, '4D': 29, '5D': 30, '6D': 31, '7D': 32, '8D': 33, '9D': 34, '10D': 35, 'JD': 36, 'QD': 37, 'KD': 38,
    # Clubs
    'AC': 39, '2C': 40, '3C': 41, '4C': 42, '5C': 43, '6C': 44, '7C': 45, '8C': 46, '9C': 47, '10C': 48, 'JC': 49, 'QC': 50, 'KC': 51
}

# Reverse mapping for class names
CLASS_NAMES = {v: k for k, v in CARD_CLASSES.items()}


class YOLOTrainer:
    """Complete YOLO training system for playing cards."""
    
    def __init__(self, dataset_path: str, output_dir: str = "training_output"):
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Training configuration
        self.config = {
            "model_size": "yolov8n",  # nano, small, medium, large, xlarge
            "epochs": 100,
            "batch_size": 16,
            "image_size": 640,
            "patience": 50,  # early stopping
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }
        
        print(f"YOLO Trainer initialized")
        print(f"Dataset: {self.dataset_path}")
        print(f"Output: {self.output_dir}")
        print(f"Device: {self.config['device']}")
    
    def detect_dataset_format(self) -> str:
        """Automatically detect dataset format."""
        print("\nDetecting dataset format...")
        
        # Check for YOLO format (images + txt files)
        jpg_files = list(self.dataset_path.glob("**/*.jpg"))
        png_files = list(self.dataset_path.glob("**/*.png"))
        txt_files = list(self.dataset_path.glob("**/*.txt"))
        
        image_files = jpg_files + png_files
        
        if image_files and txt_files:
            # Check if txt files match image files
            image_stems = {f.stem for f in image_files}
            txt_stems = {f.stem for f in txt_files if not f.name.startswith('classes')}
            
            if len(image_stems & txt_stems) > 0:
                print("SUCCESS: Detected YOLO format (images + .txt annotations)")
                return "yolo"
        
        # Check for COCO format
        json_files = list(self.dataset_path.glob("**/*.json"))
        if json_files and image_files:
            print("SUCCESS: Detected COCO format (images + .json annotations)")
            return "coco"
        
        # Check for raw images only
        if image_files and not txt_files and not json_files:
            print("SUCCESS: Detected raw images (no annotations found)")
            return "raw"
        
        # Check for folders structure
        subfolders = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        if len(subfolders) > 0:
            print("SUCCESS: Detected folder structure")
            return "folders"
        
        print("ERROR: Unknown dataset format")
        return "unknown"
    
    def prepare_yolo_dataset(self) -> Path:
        """Prepare dataset in YOLO format."""
        print("\nPreparing YOLO dataset...")
        
        yolo_dir = self.output_dir / "yolo_dataset"
        yolo_dir.mkdir(exist_ok=True)
        
        # Create YOLO directory structure
        (yolo_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
        (yolo_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
        (yolo_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
        (yolo_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
        
        dataset_format = self.detect_dataset_format()
        
        if dataset_format == "yolo":
            self._convert_yolo_format(yolo_dir)
        elif dataset_format == "coco":
            self._convert_coco_format(yolo_dir)
        elif dataset_format == "folders":
            self._convert_folder_format(yolo_dir)
        elif dataset_format == "raw":
            self._handle_raw_images(yolo_dir)
        else:
            raise ValueError(f"Unsupported dataset format: {dataset_format}")
        
        # Create data.yaml file
        self._create_data_yaml(yolo_dir)
        
        print(f"SUCCESS: YOLO dataset prepared at {yolo_dir}")
        return yolo_dir
    
    def _convert_yolo_format(self, output_dir: Path):
        """Convert existing YOLO format dataset."""
        print("Converting YOLO format dataset...")
        
        # Find all images and labels
        image_files = list(self.dataset_path.glob("**/*.jpg")) + list(self.dataset_path.glob("**/*.png"))
        
        # Split into train/val (80/20)
        split_idx = int(len(image_files) * 0.8)
        train_images = image_files[:split_idx]
        val_images = image_files[split_idx:]
        
        self._copy_files(train_images, output_dir / "images" / "train", output_dir / "labels" / "train")
        self._copy_files(val_images, output_dir / "images" / "val", output_dir / "labels" / "val")
        
        print(f"Dataset split: {len(train_images)} train, {len(val_images)} val")
    
    def _convert_coco_format(self, output_dir: Path):
        """Convert COCO format to YOLO format."""
        print("Converting COCO format dataset...")
        
        # Find annotation file
        json_files = list(self.dataset_path.glob("**/*.json"))
        if not json_files:
            raise ValueError("No JSON annotation file found")
        
        annotation_file = json_files[0]
        print(f"Using annotation file: {annotation_file}")
        
        # Load COCO annotations
        with open(annotation_file, 'r') as f:
            coco_data = json.load(f)
        
        # Convert to YOLO format
        self._coco_to_yolo(coco_data, output_dir)
    
    def _convert_folder_format(self, output_dir: Path):
        """Convert folder-based dataset (each folder = class)."""
        print("Converting folder format dataset...")
        
        all_images = []
        
        for class_folder in self.dataset_path.iterdir():
            if not class_folder.is_dir():
                continue
            
            class_name = class_folder.name
            if class_name not in CARD_CLASSES:
                print(f"WARNING: Unknown card class: {class_name}")
                continue
            
            class_id = CARD_CLASSES[class_name]
            images = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png"))
            
            for img_path in images:
                all_images.append((img_path, class_id))
        
        # Split and process
        split_idx = int(len(all_images) * 0.8)
        train_data = all_images[:split_idx]
        val_data = all_images[split_idx:]
        
        self._process_classification_data(train_data, output_dir / "images" / "train", output_dir / "labels" / "train")
        self._process_classification_data(val_data, output_dir / "images" / "val", output_dir / "labels" / "val")
        
        print(f"Dataset split: {len(train_data)} train, {len(val_data)} val")
    
    def _handle_raw_images(self, output_dir: Path):
        """Handle raw images without annotations."""
        print("WARNING: Raw images detected - manual annotation required")
        print("TIP: Consider using tools like LabelImg or Roboflow for annotation")
        
        # Copy images to train folder
        image_files = list(self.dataset_path.glob("**/*.jpg")) + list(self.dataset_path.glob("**/*.png"))
        
        for img_path in image_files:
            dest_path = output_dir / "images" / "train" / img_path.name
            shutil.copy2(img_path, dest_path)
            
            # Create empty label file
            label_path = output_dir / "labels" / "train" / (img_path.stem + ".txt")
            label_path.touch()
        
        print(f"INFO: {len(image_files)} images copied. Please annotate them manually.")
    
    def _copy_files(self, image_files: List[Path], img_dest: Path, label_dest: Path):
        """Copy image and label files to destination."""
        for img_path in image_files:
            # Copy image
            shutil.copy2(img_path, img_dest / img_path.name)
            
            # Copy corresponding label
            label_path = img_path.parent / (img_path.stem + ".txt")
            if label_path.exists():
                shutil.copy2(label_path, label_dest / label_path.name)
            else:
                # Create empty label file
                (label_dest / label_path.name).touch()
    
    def _process_classification_data(self, data: List[Tuple[Path, int]], img_dest: Path, label_dest: Path):
        """Process classification data (folder-based) to YOLO format."""
        for img_path, class_id in data:
            # Copy image
            shutil.copy2(img_path, img_dest / img_path.name)
            
            # Create YOLO label (full image = class)
            label_content = f"{class_id} 0.5 0.5 1.0 1.0\n"  # Full image bounding box
            label_path = label_dest / (img_path.stem + ".txt")
            with open(label_path, 'w') as f:
                f.write(label_content)
    
    def _coco_to_yolo(self, coco_data: dict, output_dir: Path):
        """Convert COCO annotations to YOLO format."""
        images = {img['id']: img for img in coco_data['images']}
        categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
        
        # Group annotations by image
        annotations_by_image = {}
        for ann in coco_data['annotations']:
            img_id = ann['image_id']
            if img_id not in annotations_by_image:
                annotations_by_image[img_id] = []
            annotations_by_image[img_id].append(ann)
        
        all_image_ids = list(images.keys())
        split_idx = int(len(all_image_ids) * 0.8)
        train_ids = all_image_ids[:split_idx]
        val_ids = all_image_ids[split_idx:]
        
        self._process_coco_split(train_ids, images, annotations_by_image, categories, 
                               output_dir / "images" / "train", output_dir / "labels" / "train")
        self._process_coco_split(val_ids, images, annotations_by_image, categories,
                               output_dir / "images" / "val", output_dir / "labels" / "val")
        
        print(f"COCO dataset split: {len(train_ids)} train, {len(val_ids)} val")
    
    def _process_coco_split(self, image_ids: List[int], images: dict, annotations: dict, 
                          categories: dict, img_dest: Path, label_dest: Path):
        """Process a split of COCO data."""
        for img_id in image_ids:
            img_info = images[img_id]
            img_path = self.dataset_path / img_info['file_name']
            
            if not img_path.exists():
                continue
            
            # Copy image
            shutil.copy2(img_path, img_dest / img_path.name)
            
            # Convert annotations
            label_lines = []
            if img_id in annotations:
                for ann in annotations[img_id]:
                    category_name = categories[ann['category_id']]
                    if category_name in CARD_CLASSES:
                        class_id = CARD_CLASSES[category_name]
                        
                        # Convert COCO bbox to YOLO format
                        x, y, w, h = ann['bbox']
                        img_w, img_h = img_info['width'], img_info['height']
                        
                        # YOLO format: center_x, center_y, width, height (normalized)
                        center_x = (x + w/2) / img_w
                        center_y = (y + h/2) / img_h
                        norm_w = w / img_w
                        norm_h = h / img_h
                        
                        label_lines.append(f"{class_id} {center_x:.6f} {center_y:.6f} {norm_w:.6f} {norm_h:.6f}")
            
            # Write label file
            label_path = label_dest / (img_path.stem + ".txt")
            with open(label_path, 'w') as f:
                f.write('\n'.join(label_lines))
    
    def _create_data_yaml(self, yolo_dir: Path):
        """Create data.yaml configuration file."""
        data_config = {
            'path': str(yolo_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': 52,  # Number of classes (52 cards)
            'names': list(CLASS_NAMES.values())
        }
        
        yaml_path = yolo_dir / "data.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"Created data.yaml at {yaml_path}")
    
    def train_model(self, yolo_dataset_dir: Path) -> Path:
        """Train YOLO model on prepared dataset."""
        if not ULTRALYTICS_AVAILABLE:
            raise RuntimeError("Ultralytics not available. Install with: pip install ultralytics")
        
        print(f"\nStarting YOLO training...")
        print(f"Configuration:")
        for key, value in self.config.items():
            print(f"   {key}: {value}")
        
        # Initialize model
        model_name = f"{self.config['model_size']}.pt"
        model = YOLO(model_name)
        
        # Training arguments
        train_args = {
            'data': str(yolo_dataset_dir / "data.yaml"),
            'epochs': self.config['epochs'],
            'batch': self.config['batch_size'],
            'imgsz': self.config['image_size'],
            'patience': self.config['patience'],
            'device': self.config['device'],
            'project': str(self.output_dir),
            'name': f"cards_yolo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'save': True,
            'save_period': 10,  # Save checkpoint every 10 epochs
            'cache': True,
            'workers': 4,
            'verbose': True
        }
        
        print(f"Training arguments: {train_args}")
        
        # Start training
        results = model.train(**train_args)
        
        # Get best model path
        best_model_path = Path(results.save_dir) / "weights" / "best.pt"
        
        print(f"SUCCESS: Training completed!")
        print(f"Best model saved to: {best_model_path}")
        
        return best_model_path
    
    def validate_model(self, model_path: Path, yolo_dataset_dir: Path):
        """Validate trained model."""
        print(f"\nValidating model...")
        
        model = YOLO(str(model_path))
        
        # Run validation
        results = model.val(
            data=str(yolo_dataset_dir / "data.yaml"),
            device=self.config['device']
        )
        
        print(f"Validation Results:")
        print(f"   mAP50: {results.box.map50:.3f}")
        print(f"   mAP50-95: {results.box.map:.3f}")
        
        return results
    
    def test_model(self, model_path: Path, test_image_path: str):
        """Test model on a single image."""
        print(f"\nTesting model on {test_image_path}...")
        
        model = YOLO(str(model_path))
        
        # Run inference
        results = model(test_image_path)
        
        # Display results
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                print(f"Detected {len(boxes)} cards:")
                for box in boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    card_name = CLASS_NAMES.get(class_id, f"Unknown_{class_id}")
                    print(f"   {card_name}: {confidence:.3f}")
            else:
                print("No cards detected")
        
        # Save result image
        result_path = self.output_dir / f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        results[0].save(str(result_path))
        print(f"Result saved to: {result_path}")
        
        return results


def main():
    """Main training interface."""
    parser = argparse.ArgumentParser(description="Train YOLO model for playing cards")
    parser.add_argument("dataset_path", help="Path to dataset directory")
    parser.add_argument("--output", "-o", default="training_output", help="Output directory")
    parser.add_argument("--model-size", choices=["n", "s", "m", "l", "x"], default="n", 
                       help="Model size (nano/small/medium/large/xlarge)")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--image-size", type=int, default=640, help="Input image size")
    parser.add_argument("--test-image", help="Test image path after training")
    parser.add_argument("--skip-training", action="store_true", help="Skip training, only prepare dataset")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = YOLOTrainer(args.dataset_path, args.output)
    
    # Update configuration
    trainer.config.update({
        "model_size": f"yolov8{args.model_size}",
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "image_size": args.image_size
    })
    
    try:
        # Prepare dataset
        yolo_dataset_dir = trainer.prepare_yolo_dataset()
        
        if args.skip_training:
            print("✅ Dataset preparation completed. Skipping training.")
            return
        
        # Train model
        best_model_path = trainer.train_model(yolo_dataset_dir)
        
        # Validate model
        trainer.validate_model(best_model_path, yolo_dataset_dir)
        
        # Test on single image if provided
        if args.test_image:
            trainer.test_model(best_model_path, args.test_image)
        
        print(f"\n🎉 Training pipeline completed successfully!")
        print(f"🏆 Best model: {best_model_path}")
        
        # Copy best model to project models directory
        project_model_path = Path("models/playing_cards_yolo.pt")
        project_model_path.parent.mkdir(exist_ok=True)
        shutil.copy2(best_model_path, project_model_path)
        print(f"📋 Model copied to: {project_model_path}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())