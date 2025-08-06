# 🚀 QUICK START - Poker AI MVP

## ⚡ Option 1: Automatic Setup (Recommended)

**Double-click:** `install_and_run.bat`

This will:
1. ✅ Check Python installation
2. ✅ Create virtual environment  
3. ✅ Install all dependencies
4. ✅ Setup YOLO model (optional)
5. ✅ Launch the application

## ⚡ Option 2: Manual Setup

### 1. Install Python 3.11+
Download from: https://www.python.org/downloads/
**⚠️ Make sure to check "Add Python to PATH"**

### 2. Install Dependencies
```bash
# Double-click: setup_python.bat
# OR manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 3. Run Application
```bash
python run.py
```

## 🎯 First Time Setup

### 1. Open Poker Client
- Launch your preferred poker client
- Join a 3-player table

### 2. Calibrate Regions
- Click **"🎯 Safe Calibrate"** in dashboard
- Select poker client window region
- Define detection areas for cards, chips, players

### 3. Start Vision System
- Click **"▶️ START"** to begin data collection
- Monitor live detection in dashboard
- Export collected data with **"📊 Export"**

## 🔧 Troubleshooting

### Python Not Found
```bash
# Add Python to PATH or reinstall with PATH option
# Verify with: python --version
```

### Missing Dependencies
```bash
# Activate environment first
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### YOLO Model Issues
```bash
# Optional - skip for basic functionality
python setup_cards_model.py
# Choose option 1 for quick setup
```

## 📁 Directory Structure
```
poker_ai_mvp/
├── data/           # Database files (auto-created)
├── logs/           # Application logs (auto-created)  
├── models/         # YOLO models (optional)
├── config/         # Settings files (pre-configured)
└── src/            # Source code
```

## 🎮 Usage

1. **Dashboard**: Real-time monitoring and control
2. **Debug Tools**: Vision testing and calibration
3. **Data Export**: JSON/CSV export for analysis
4. **Safe Operation**: 100% passive observation

Ready to start! 🎉