# 🚀 How to Run Poker AI MVP

## Quick Start (Windows)

### Step 1: Open Command Prompt
- Press `Win + R`, type `cmd`, press Enter
- Or search "Command Prompt" in Start Menu

### Step 2: Navigate to Project
```cmd
cd "C:\Users\McGrady\Desktop\yes\poker_ai_mvp"
```

### Step 3: Run the Setup Script
```cmd
setup_and_run.bat
```

**OR** if that doesn't work, do it manually:

### Manual Setup (if batch file fails)

1. **Create Virtual Environment:**
```cmd
python -m venv venv
```

2. **Activate Virtual Environment:**
```cmd
venv\Scripts\activate
```

3. **Install Dependencies:**
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Setup YOLO Model (Optional but Recommended):**
```cmd
python setup_cards_model.py
```
Choose option 1 for quick start (downloads base YOLO automatically)

5. **Run the Application:**
```cmd
python run.py
```

## What to Expect

1. **Installation**: First run will install ~2GB of dependencies (PyTorch, OpenCV, etc.)
2. **GUI Launch**: A tkinter window will open showing the dashboard
3. **System Status**: Initially shows "INACTIVE" status
4. **Start Button**: Click "▶️ START" to begin vision capture

## Dashboard Features

- **Live Game State**: Shows current hand, phase, pot, timer
- **Vision Stats**: Detection accuracy, FPS, processing time
- **Players**: Stack sizes and hole cards (when visible)
- **Activity Log**: Real-time system events
- **Session Stats**: Uptime, hands processed, performance

## Important Notes

⚠️ **Make sure your poker client is running and visible before clicking START**

⚠️ **The system captures your entire screen by default** - adjust regions in `config/settings.json` if needed

⚠️ **First run may be slow** while downloading ML models

## Troubleshooting

If you get errors:

1. **Python not found**: Install Python 3.11+ from python.org
2. **Permission errors**: Run Command Prompt as Administrator
3. **Installation fails**: Check internet connection
4. **GUI doesn't show**: Install tkinter: `pip install tk`

## Next Steps

Once running:
1. Click START to begin vision capture
2. Open your poker client
3. Watch the dashboard update in real-time
4. Use EXPORT to save collected data

The system is designed to run continuously while you play poker, collecting training data for future AI development.