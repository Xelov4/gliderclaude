# 🎯 YOLO Training Guide for Playing Cards

## 🚀 Quick Start

### **Step 1: Prepare Your Dataset**

First, tell me about your dataset:

1. **Where is your dataset located?**
2. **What format is it in?**
   - YOLO format (images + .txt files)
   - COCO format (images + .json file)
   - Folder structure (one folder per card type)
   - Raw images only

3. **Dataset size and characteristics?**

### **Step 2: Install Dependencies**

```bash
# Install training dependencies
pip install ultralytics torch torchvision
pip install pyyaml opencv-python
```

### **Step 3: Train the Model**

```bash
# Basic training (auto-detects dataset format)
python train_yolo_model.py /path/to/your/dataset

# Advanced training with custom parameters
python train_yolo_model.py /path/to/your/dataset \
    --model-size s \
    --epochs 200 \
    --batch-size 32 \
    --image-size 640
```

## 📊 Supported Dataset Formats

### **Format 1: YOLO Format (Recommended)**
```
dataset/
├── image1.jpg
├── image1.txt    # YOLO annotations
├── image2.jpg
├── image2.txt
└── ...
```

**YOLO Annotation Format (.txt files):**
```
class_id center_x center_y width height
0 0.5 0.3 0.2 0.4
1 0.7 0.6 0.15 0.3
```

### **Format 2: COCO Format**
```
dataset/
├── images/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── annotations.json    # COCO format
```

### **Format 3: Folder Structure**
```
dataset/
├── AS/           # Ace of Spades
│   ├── img1.jpg
│   └── img2.jpg
├── 2S/           # 2 of Spades
│   ├── img1.jpg
│   └── img2.jpg
└── ...
```

### **Format 4: Raw Images**
```
dataset/
├── image1.jpg
├── image2.jpg
└── ...
```
*Note: Raw images require manual annotation*

## 🎯 Playing Card Classes

The system supports all 52 standard playing cards:

**Spades:** AS, 2S, 3S, 4S, 5S, 6S, 7S, 8S, 9S, 10S, JS, QS, KS
**Hearts:** AH, 2H, 3H, 4H, 5H, 6H, 7H, 8H, 9H, 10H, JH, QH, KH  
**Diamonds:** AD, 2D, 3D, 4D, 5D, 6D, 7D, 8D, 9D, 10D, JD, QD, KD
**Clubs:** AC, 2C, 3C, 4C, 5C, 6C, 7C, 8C, 9C, 10C, JC, QC, KC

## ⚙️ Training Parameters

### **Model Sizes:**
- **nano (n)**: Fastest, smallest, lower accuracy
- **small (s)**: Good balance of speed/accuracy  
- **medium (m)**: Better accuracy, slower
- **large (l)**: High accuracy, requires more resources
- **xlarge (x)**: Highest accuracy, slowest

### **Recommended Settings:**

#### **Small Dataset (<1000 images):**
```bash
python train_yolo_model.py dataset/ \
    --model-size n \
    --epochs 150 \
    --batch-size 8 \
    --image-size 416
```

#### **Medium Dataset (1000-5000 images):**
```bash
python train_yolo_model.py dataset/ \
    --model-size s \
    --epochs 100 \
    --batch-size 16 \
    --image-size 640
```

#### **Large Dataset (5000+ images):**
```bash
python train_yolo_model.py dataset/ \
    --model-size m \
    --epochs 80 \
    --batch-size 32 \
    --image-size 640
```

## 🔍 Dataset Quality Guidelines

### **Image Requirements:**
- **Resolution**: Minimum 416x416, recommended 640x640 or higher
- **Format**: JPG or PNG
- **Quality**: Clear, unblurred images
- **Lighting**: Varied lighting conditions for robustness

### **Annotation Quality:**
- **Accurate bounding boxes**: Tight around each card
- **Complete annotations**: Every visible card should be labeled
- **Consistent labeling**: Use standard card names (AS, KH, etc.)

### **Dataset Balance:**
- **All cards represented**: Include all 52 card types if possible
- **Varied scenarios**: Different backgrounds, angles, lighting
- **Multiple cards per image**: Include images with 2-5+ cards
- **Minimum per class**: At least 20-50 examples per card type

## 📈 Training Process

### **What Happens During Training:**

1. **Dataset Analysis**: Auto-detects format and validates
2. **Data Preparation**: Converts to YOLO format, splits train/val
3. **Model Initialization**: Downloads base YOLO model
4. **Training Loop**: Trains for specified epochs
5. **Validation**: Tests on validation set each epoch
6. **Model Saving**: Saves best model based on validation performance

### **Training Output:**
```
training_output/
├── yolo_dataset/           # Prepared dataset
│   ├── images/
│   │   ├── train/
│   │   └── val/
│   ├── labels/
│   │   ├── train/
│   │   └── val/
│   └── data.yaml
└── cards_yolo_YYYYMMDD_HHMMSS/    # Training results
    ├── weights/
    │   ├── best.pt         # Best model
    │   └── last.pt         # Last epoch
    ├── results.png         # Training curves
    └── confusion_matrix.png
```

## 🧪 Testing Your Model

### **Test on Single Image:**
```bash
python train_yolo_model.py dataset/ --test-image test_image.jpg
```

### **Manual Testing:**
```python
from ultralytics import YOLO

# Load your trained model
model = YOLO('models/playing_cards_yolo.pt')

# Test on image
results = model('test_image.jpg')
results[0].show()  # Display results
```

## 📊 Evaluation Metrics

### **Key Metrics:**
- **mAP50**: Mean Average Precision at IoU threshold 0.5
- **mAP50-95**: Mean Average Precision averaged over IoU 0.5-0.95
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)

### **Good Performance Targets:**
- **mAP50 > 0.8**: Excellent detection performance
- **mAP50 > 0.6**: Good performance for most applications
- **mAP50 > 0.4**: Acceptable for initial testing

## 🚨 Troubleshooting

### **Common Issues:**

#### **Out of Memory:**
```bash
# Reduce batch size
--batch-size 8

# Use smaller model
--model-size n

# Reduce image size
--image-size 416
```

#### **Poor Performance:**
- **More data**: Collect more training images
- **Better annotations**: Check annotation accuracy
- **Data augmentation**: Enable in training config
- **Longer training**: Increase epochs

#### **Slow Training:**
- **GPU**: Ensure CUDA is properly installed
- **Smaller model**: Use nano or small size
- **Reduce image size**: Use 416 instead of 640

#### **No Cards Detected:**
- **Check classes**: Ensure class names match
- **Lower threshold**: Reduce confidence threshold
- **More training**: Model may need more epochs

## 🎯 Integration with Poker AI

After successful training, the model will be automatically copied to:
```
models/playing_cards_yolo.pt
```

The poker AI system will automatically use this trained model for card detection.

## 📞 Getting Help

If you encounter issues:

1. **Check dataset format**: Use `--skip-training` to test dataset preparation
2. **Validate annotations**: Manually inspect a few converted files
3. **Start small**: Try with a subset of your data first
4. **Monitor training**: Watch the training curves for overfitting/underfitting

---

**Ready to start training? Just run the script with your dataset path! 🚀**