#!/usr/bin/env python3
"""
Playing Cards Model Setup Script

Helps set up YOLO model for playing cards detection.
Integrates with existing cards dataset.
"""

import os
import sys
import shutil
from pathlib import Path
import yaml
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def setup_cards_dataset():
    """Setup the playing cards dataset for YOLO training."""
    logger.info("Setting up playing cards dataset...")
    
    # Check if dataset exists
    dataset_path = Path("C:/Users/McGrady/.cache/kagglehub/datasets/andy8744/playing-cards-object-detection-dataset/versions/4")
    
    if not dataset_path.exists():
        logger.error(f"Cards dataset not found at: {dataset_path}")
        logger.info("Please ensure the dataset is downloaded from Kaggle")
        return False
    
    # Create models directory structure
    models_dir = Path("models")
    cards_dir = models_dir / "cards_dataset"
    cards_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Copy dataset files
        logger.info("Copying dataset files...")
        
        # Copy the dataset (this might be large - show progress)
        if not (cards_dir / "train").exists():
            logger.info("Copying training data... (this may take a while)")
            shutil.copytree(dataset_path, cards_dir, dirs_exist_ok=True)
        
        logger.info("Dataset copied successfully")
        
        # Create YOLO data configuration
        create_yolo_config(cards_dir)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup dataset: {e}")
        return False


def create_yolo_config(dataset_dir: Path):
    """Create YOLO data configuration file."""
    logger.info("Creating YOLO configuration...")
    
    # Analyze dataset structure
    train_dir = dataset_dir / "train"
    val_dir = dataset_dir / "valid" if (dataset_dir / "valid").exists() else dataset_dir / "val"
    
    # Count classes (assuming YOLO format labels)
    classes = set()
    if train_dir.exists():
        labels_dir = train_dir / "labels" if (train_dir / "labels").exists() else train_dir
        for label_file in labels_dir.glob("*.txt"):
            try:
                with open(label_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            class_id = int(line.split()[0])
                            classes.add(class_id)
            except:
                continue
    
    # Create class names (you'll need to customize this based on your dataset)
    if not classes:
        # Default 52 card classes
        class_names = []
        for suit in ["spades", "hearts", "diamonds", "clubs"]:
            for rank in ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]:
                class_names.append(f"{rank}_of_{suit}")
    else:
        # Use detected classes
        class_names = [f"card_class_{i}" for i in sorted(classes)]
    
    # Create YOLO data.yaml
    data_config = {
        'path': str(dataset_dir.absolute()),
        'train': 'train/images' if (train_dir / "images").exists() else 'train',
        'val': 'valid/images' if (val_dir / "images").exists() else 'valid' if val_dir.exists() else 'train',
        'nc': len(class_names),
        'names': class_names
    }
    
    config_path = dataset_dir / "data.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    logger.info(f"Created YOLO config with {len(class_names)} classes")
    logger.info(f"Config saved to: {config_path}")
    
    return config_path


def download_base_model():
    """Download base YOLO model."""
    logger.info("Setting up base YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Download YOLOv8 nano model
        model = YOLO('yolov8n.pt')
        
        # Save to models directory
        base_model_path = models_dir / "yolov8n.pt"
        model.save(str(base_model_path))
        
        logger.info(f"Base YOLO model saved to: {base_model_path}")
        return str(base_model_path)
        
    except ImportError:
        logger.error("ultralytics not installed. Run: pip install ultralytics")
        return None
    except Exception as e:
        logger.error(f"Failed to download base model: {e}")
        return None


def train_cards_model(data_config_path: str, epochs: int = 50):
    """Train YOLO model on playing cards dataset."""
    logger.info("Starting YOLO training...")
    
    try:
        from ultralytics import YOLO
        
        # Load base model
        model = YOLO('yolov8n.pt')
        
        # Train on cards dataset
        logger.info(f"Training for {epochs} epochs...")
        results = model.train(
            data=data_config_path,
            epochs=epochs,
            imgsz=640,
            batch=16,
            name='playing_cards',
            project='models/training'
        )
        
        # Save trained model
        trained_model_path = Path("models/playing_cards_yolo.pt")
        model.save(str(trained_model_path))
        
        logger.info(f"Training complete! Model saved to: {trained_model_path}")
        return str(trained_model_path)
        
    except ImportError:
        logger.error("ultralytics not installed. Run: pip install ultralytics")
        return None
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return None


def main():
    """Main setup function."""
    print("🎯 Playing Cards YOLO Setup")
    print("=" * 40)
    
    choice = input("""
Choose setup option:
1. Quick start (download base YOLO model only)
2. Full setup (use your cards dataset)
3. Train custom model (requires dataset + time)

Enter choice (1-3): """).strip()
    
    if choice == "1":
        logger.info("Quick start setup...")
        model_path = download_base_model()
        if model_path:
            print(f"✅ Setup complete! Base model ready at: {model_path}")
            print("   Note: This provides basic object detection only")
        else:
            print("❌ Setup failed!")
            
    elif choice == "2":
        logger.info("Full dataset setup...")
        if setup_cards_dataset():
            print("✅ Dataset setup complete!")
            print("   - Dataset copied to models/cards_dataset/")
            print("   - YOLO config created")
            print("   - Ready for training or inference")
        else:
            print("❌ Dataset setup failed!")
            
    elif choice == "3":
        logger.info("Training setup...")
        
        # First setup dataset
        if not setup_cards_dataset():
            print("❌ Dataset setup failed!")
            return
        
        # Then train
        data_config = "models/cards_dataset/data.yaml"
        epochs = int(input("Enter number of training epochs (default 50): ") or "50")
        
        model_path = train_cards_model(data_config, epochs)
        if model_path:
            print(f"✅ Training complete! Model ready at: {model_path}")
        else:
            print("❌ Training failed!")
    
    else:
        print("Invalid choice!")
        return
    
    print("\n🚀 Next steps:")
    print("1. Run the main application: python run.py")
    print("2. Use 'Safe Debug' button to test card detection")
    print("3. Calibrate regions for your poker client")
    print("4. Start collecting training data!")


if __name__ == "__main__":
    main()