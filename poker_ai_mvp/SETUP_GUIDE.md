# 🎯 Poker AI MVP - Complete Setup Guide

## 🚀 How Window Detection & Targeting Works

### **Automatic Window Detection**
1. **🎯 Calibrate Button**: Click to select your poker client window
2. **Window Selector**: Shows all open windows with titles and sizes
3. **Target Selection**: Choose your poker client from the list
4. **Region Calibration**: Click and drag to define areas for cards, chips, etc.

### **Smart Region Detection**
The system needs to know WHERE to look for:
- **Community Cards** (center of table)
- **Player Information** (names, stacks, cards)
- **Pot Display** (total pot amount)
- **Timer** (action countdown)
- **UI Elements** (buttons, betting slider)

---

## 🔍 Debug & Fine-Tuning Tools

### **🔍 Debug Button** - Vision Debugging
- **Load Screenshots**: Test detection on saved images
- **Live Capture**: Real-time screen analysis
- **Detection Testing**: See what cards/text are detected
- **Confidence Adjustment**: Tune detection thresholds
- **Annotation Tools**: Manually label images for training

### **Debug Features:**
- ✅ **Card Detection Visualization**: Green circles show detected cards
- ✅ **OCR Results**: Blue boxes around detected text
- ✅ **Confidence Scores**: See detection accuracy
- ✅ **Region Overlays**: Visual boundaries for all detection areas
- ✅ **Real-time Adjustment**: Change thresholds and see results instantly

---

## 📋 Step-by-Step Setup Process

### **Phase 1: Installation** ⏱️ ~10 minutes
```bash
cd "C:\Users\McGrady\Desktop\yes\poker_ai_mvp"
setup_and_run.bat
```

### **Phase 2: Window Targeting** ⏱️ ~5 minutes
1. **Open your poker client** first
2. **Launch Poker AI MVP**
3. **Click "🎯 Calibrate"**
4. **Select your poker window** from the list
5. **Define regions** by clicking and dragging:
   - Community cards area
   - Each player position
   - Pot display
   - Timer location

### **Phase 3: Testing & Tuning** ⏱️ ~15 minutes
1. **Click "🔍 Debug"** to open debug tools
2. **Take a screenshot** of your poker client
3. **Test card detection** - adjust confidence if needed
4. **Test OCR** - verify it reads chip amounts correctly
5. **Parse game state** - check complete detection

### **Phase 4: Live Operation** ⏱️ Continuous
1. **Click "▶️ START"** to begin live capture
2. **Monitor dashboard** for detection accuracy
3. **Watch activity log** for any errors
4. **Export data** when you have enough samples

---

## 🎛️ Fine-Tuning Parameters

### **Card Detection Settings**
```json
"card_detection": {
    "confidence_threshold": 0.8,  // Lower = more sensitive (0.1-1.0)
    "nms_threshold": 0.4          // Overlap filtering (0.1-0.9)
}
```

### **Text Recognition Settings**
```json
"text_recognition": {
    "confidence_threshold": 0.7   // Lower = more text detected (0.1-1.0)
}
```

### **Performance Settings**
```json
"screen_capture": {
    "fps": 30                     // Lower = less CPU usage (10-60)
}
```

---

## 🔧 Common Issues & Solutions

### **❌ "No cards detected"**
**Causes & Fixes:**
- **Card style different**: Lower confidence threshold to 0.6-0.7
- **Poor lighting**: Adjust screen brightness
- **Wrong region**: Recalibrate community card area
- **YOLO model missing**: Check `models/` folder

### **❌ "OCR not reading numbers"**
**Causes & Fixes:**
- **Font scaling**: Increase region size by 20-30%
- **Font style**: Lower OCR confidence to 0.5-0.6
- **Resolution**: Ensure 1920x1080 or adjust regions proportionally
- **Color contrast**: Check text is clearly visible

### **❌ "Wrong window captured"**
**Causes & Fixes:**
- **Multiple monitors**: Recalibrate and select correct window
- **Window moved**: Re-run calibration
- **Poker client updated**: May need region adjustment

### **❌ "System too slow"**
**Causes & Fixes:**
- **Reduce FPS**: Change from 30 to 15-20 FPS
- **Lower confidence**: Reduce detection thresholds
- **Close apps**: Free up CPU/GPU resources
- **Check GPU usage**: Ensure PyTorch uses your GTX 1080 Ti

---

## 📊 Understanding the Dashboard

### **Live Game State Panel**
- **Hand ID**: Unique identifier for current hand
- **Phase**: preflop/flop/turn/river
- **Pot**: Total chips in the pot
- **Timer**: Countdown for current player action
- **Community Cards**: Cards on the board (e.g., "4♦ 10♥ 10♣")

### **Vision Stats Panel**
- **🎯 Cards**: How many cards detected out of expected
- **📝 Text**: OCR accuracy percentage
- **⚡ Speed**: Processing frames per second
- **🧠 Processing**: Milliseconds per frame
- **❌ Errors**: Failed detections in last hour

### **Players Panel**
- **Position indicators**: Shows which seat each player occupies
- **Stack sizes**: Current chip counts
- **Hole cards**: Your cards (when visible)
- **Current player**: Highlighted when it's their turn
- **Action status**: ACTIVE/FOLDED/CURRENT

### **Activity Log**
- **Real-time events**: System start/stop, errors, detections
- **Timestamped entries**: Precise timing of all events
- **Error tracking**: Detailed error messages for debugging
- **Auto-scroll**: Always shows latest activity

---

## 🎯 Optimization Tips

### **For Maximum Accuracy:**
1. **Good lighting**: Ensure poker client is clearly visible
2. **Clean background**: Avoid overlapping windows
3. **Stable positioning**: Don't move poker client window
4. **Full screen**: Use poker client in full-screen or large window
5. **High contrast**: Adjust poker client themes for clarity

### **For Best Performance:**
1. **Close background apps**: Free up system resources
2. **Reduce FPS**: Lower from 30 to 20 if system struggles
3. **Optimize regions**: Make detection areas as small as possible
4. **GPU utilization**: Ensure PyTorch uses your graphics card

### **For Training Data Quality:**
1. **Diverse scenarios**: Capture different hand phases
2. **Multiple opponents**: Different player counts and styles  
3. **Various stakes**: Different chip amounts and bet sizes
4. **Long sessions**: Capture 1000+ hands for good dataset
5. **Manual validation**: Use debug tools to verify accuracy

---

## 🔄 Troubleshooting Workflow

### **If Detection Fails:**
1. **🔍 Debug Tools** → Load current screenshot
2. **Adjust confidence** sliders in debug interface
3. **Test detection** on the screenshot
4. **Save working values** to settings.json
5. **Restart system** to apply changes

### **If Performance Issues:**
1. **Check Task Manager** → GPU/CPU usage
2. **Reduce FPS** in settings.json
3. **Close other applications**
4. **Monitor dashboard** statistics
5. **Check logs** for error patterns

### **If Data Quality Issues:**
1. **Export current data** for analysis
2. **Review detection confidence** in database
3. **Manually annotate** problem cases
4. **Retrain models** with new data (future feature)

---

## 📈 Success Metrics

### **System is Working Well When:**
- ✅ **Card detection**: >95% accuracy (5/5 cards detected)
- ✅ **OCR accuracy**: >90% for chip amounts
- ✅ **Frame rate**: Steady 25-30 FPS
- ✅ **Processing time**: <150ms per frame
- ✅ **Error rate**: <5% failed detections
- ✅ **Uptime**: >8 hours continuous operation

### **Ready for AI Training When:**
- ✅ **10,000+ hands** of clean data collected
- ✅ **All game phases** represented (preflop through river)
- ✅ **Multiple scenarios**: Various pot sizes, player actions
- ✅ **High confidence**: >98% detection accuracy sustained
- ✅ **Validated data**: Manual verification of key samples

The system is designed to run **continuously** while you play, building a comprehensive training dataset for future AI development! 🎮🤖