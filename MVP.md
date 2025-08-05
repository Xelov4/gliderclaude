# Poker AI - MVP Specification
## Vision Recognition & Data Logging System

---

## 🎯 MVP Scope

**What's Included:**
- ✅ Real-time screen capture and vision recognition
- ✅ Complete game state detection and parsing
- ✅ Real-time dashboard with live monitoring
- ✅ Comprehensive data logging to SQLite database
- ✅ Training data collection and annotation tools

**What's NOT Included:**
- ❌ No AI decision making
- ❌ No automated actions/input simulation
- ❌ No poker strategy implementation
- ❌ No opponent modeling

**Goal**: Establish a robust vision pipeline that captures 100% accurate game data for future AI training.

---

## 🖥️ System Architecture (MVP)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Screen        │───▶│   Vision        │───▶│    Data         │
│   Capture       │    │   Processing    │    │   Logger        │
│   (30 FPS)      │    │   Pipeline      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Game States │ │ Vision Logs │ │ Performance │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 tkinter Dashboard                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Live View   │ │ Statistics  │ │ Performance │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Vision Pipeline Detailed

### Target Elements (Based on Client Screenshot)

**Game Table Elements:**
- **Community Cards**: Center area (4♦, 10♥, 10♣ in screenshot)
- **Player Positions**: 3 fixed positions around table
- **Pot Amount**: Center display (80 chips in screenshot)
- **Timer**: Top right countdown (01:35 format)

**Player Information per Position:**
- **Avatar/Name**: Player identification (chris48, Routine, xlv)
- **Stack Size**: Chip count below name (500, 460, 460)
- **Hole Cards**: Player's private cards (Q♦, 4♥ visible)
- **Current Bet**: Amount in front of player
- **Action Status**: Current player indicator

**UI Elements:**
- **Action Buttons**: Bottom area (Fold, Check, Bet)
- **Betting Controls**: Slider with percentages (35%, 65%, Pot, All-in)
- **Bet Amount**: Input field (20 in screenshot)
- **Hand Strength**: Text indicator ("DEUX PAIRES")

### Processing Pipeline
```
1. Screen Capture (mss) → Raw Image (1920x1080)
2. Region Extraction → Crop specific areas
3. Parallel Processing:
   ├── Card Detection (YOLOv9) → Card positions + confidence
   ├── Text Recognition (PaddleOCR) → Numbers and names
   ├── UI Detection → Button states and positions
   └── Color Analysis → Player status indicators
4. Data Validation → Cross-reference detected elements
5. State Reconstruction → Complete GameState object
6. Database Storage → SQLite with timestamp
```

---

## 📊 Data Models

### Core Data Structures
```python
@dataclass
class Card:
    rank: str          # "A", "K", "Q", "J", "10", "9", ..., "2"
    suit: str          # "♠", "♥", "♦", "♣"
    confidence: float  # 0.0 to 1.0
    position: Tuple[int, int]  # (x, y) coordinates
    
@dataclass 
class Player:
    position: int      # 0, 1, 2 (clockwise from bottom)
    name: str          # Player username
    stack_size: int    # Current chip count
    hole_cards: List[Card]  # Private cards (empty if not visible)
    current_bet: int   # Amount bet this round
    is_active: bool    # Currently in hand
    is_current: bool   # Current player to act

@dataclass
class GameState:
    timestamp: datetime
    hand_id: str              # Unique hand identifier
    game_phase: str           # "preflop", "flop", "turn", "river"
    pot_size: int            # Total pot amount
    community_cards: List[Card]  # Board cards
    players: List[Player]     # All player states
    timer_remaining: int      # Seconds left for action
    available_actions: List[str]  # ["fold", "check", "bet", "call", "raise"]
    betting_options: Dict     # Slider values and limits
    
@dataclass
class VisionMetrics:
    timestamp: datetime
    processing_time_ms: int
    frame_rate: float
    card_detection_confidence: float
    text_ocr_confidence: float
    total_elements_detected: int
    failed_detections: List[str]
```

---

## 🗄️ Database Schema

### SQLite Tables
```sql
-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_hands INTEGER DEFAULT 0,
    total_frames_processed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active'  -- 'active', 'paused', 'completed'
);

-- Hands table  
CREATE TABLE hands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    hand_number INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    final_pot INTEGER,
    winner_position INTEGER,
    hand_strength TEXT,  -- "DEUX PAIRES", "FLUSH", etc.
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

-- Game states (multiple snapshots per hand)
CREATE TABLE game_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hand_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    game_phase TEXT,  -- preflop, flop, turn, river
    pot_size INTEGER,
    community_cards TEXT,  -- JSON array of cards
    timer_remaining INTEGER,
    current_player_position INTEGER,
    FOREIGN KEY (hand_id) REFERENCES hands (id)
);

-- Player states (one per player per game state)
CREATE TABLE player_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER,
    position INTEGER,  -- 0, 1, 2
    name TEXT,
    stack_size INTEGER,
    hole_cards TEXT,  -- JSON array, empty if not visible
    current_bet INTEGER,
    is_active BOOLEAN,
    is_current BOOLEAN,
    FOREIGN KEY (game_state_id) REFERENCES game_states (id)
);

-- Vision performance metrics
CREATE TABLE vision_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    frame_rate REAL,
    card_detection_confidence REAL,
    text_ocr_confidence REAL,
    elements_detected INTEGER,
    elements_failed INTEGER,
    error_details TEXT  -- JSON array of failed elements
);

-- Training annotations (for future ML training)
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT,
    timestamp TIMESTAMP,
    ground_truth TEXT,  -- JSON with correct labels
    model_prediction TEXT,  -- JSON with model output
    confidence_scores TEXT,  -- JSON with confidence values
    is_validated BOOLEAN DEFAULT FALSE
);
```

---

## 🖼️ Dashboard Interface (tkinter)

### Main Window Layout (1200x800 pixels)
```
┌────────────────────────────────────────────────────────────────┐
│ Poker AI Vision Monitor v1.0                     ●🟢 RUNNING   │
├────────────────────────────────────────────────────────────────┤
│ ┌─── Live Game State ─────────────┐ ┌─── Vision Stats ────────┐ │
│ │ Hand #1847 | Phase: Flop       │ │ 🎯 Cards: 5/5 detected  │ │
│ │ Pot: 80 chips | Timer: 01:35   │ │ 📝 Text: 98.2% accuracy │ │
│ │                                │ │ ⚡ Speed: 29.8 FPS      │ │
│ │ Community: 4♦ 10♥ 10♣          │ │ 🧠 Processing: 87ms     │ │
│ │                                │ │ ❌ Errors: 2 last hour  │ │
│ └────────────────────────────────┘ └─────────────────────────┘ │
│ ┌─── Player States ──────────────┐ ┌─── Recent Activity ────┐ │
│ │ 👤 chris48 (Pos 0)  [CURRENT] │ │ 12:34:15 - Hand started │ │
│ │    Stack: 500 | Bet: 0         │ │ 12:34:16 - Cards dealt  │ │
│ │    Cards: Q♦ 4♥               │ │ 12:34:45 - Flop shown   │ │
│ │                                │ │ 12:34:46 - chris48 turn │ │
│ │ 👤 Routine (Pos 1)             │ │ 12:34:58 - Timer at :30 │ │
│ │    Stack: 460 | Bet: 20        │ │                         │ │
│ │    Cards: ?? ??                │ │ [Auto-scroll enabled]   │ │
│ │                                │ │                         │ │
│ │ 👤 xlv (Pos 2)                 │ │                         │ │
│ │    Stack: 460 | Bet: 0         │ │                         │ │
│ │    Cards: ?? ??                │ │                         │ │
│ └────────────────────────────────┘ └─────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│ ┌─── Session Statistics ─────────────────────────────────────┐  │
│ │ ⏱️ Uptime: 2h 15m | 📊 Hands: 1847 | 💾 Data: 245MB      │  │
│ │ 🎯 Avg Accuracy: 97.8% | ⚡ Avg FPS: 29.2 | 🐛 Errors: 23 │  │
│ └───────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│ [▶️ START] [⏸️ PAUSE] [⏹️ STOP] [⚙️ Settings] [📊 Export] [📈 Charts] │
└────────────────────────────────────────────────────────────────┘
```

### Widget Specifications
- **Real-time Updates**: All values update every 100ms
- **Color Coding**: Green=good, Yellow=warning, Red=error
- **Progress Bars**: For confidence scores and performance metrics
- **Scrollable Logs**: Last 100 activities with timestamps
- **Export Buttons**: CSV, JSON data export functionality

---

## ⚙️ Configuration System

### Settings File (settings.json)
```json
{
  "screen_capture": {
    "monitor": 0,
    "fps": 30,
    "region": {
      "x": 0,
      "y": 0, 
      "width": 1920,
      "height": 1080
    }
  },
  "vision": {
    "card_detection": {
      "model_path": "models/yolov9_cards.pt",
      "confidence_threshold": 0.8,
      "nms_threshold": 0.4
    },
    "text_recognition": {
      "ocr_language": "en", 
      "confidence_threshold": 0.7
    }
  },
  "database": {
    "path": "data/poker_vision.db",
    "backup_frequency": 3600,
    "retention_days": 30
  },
  "dashboard": {
    "update_frequency_ms": 100,
    "max_log_entries": 1000,
    "auto_scroll": true
  },
  "game_client": {
    "window_title": "Poker Client",
    "table_regions": {
      "community_cards": {"x": 530, "y": 315, "w": 270, "h": 120},
      "pot_display": {"x": 810, "y": 260, "w": 100, "h": 40},
      "timer": {"x": 1160, "y": 60, "w": 100, "h": 40},
      "player_0": {"x": 475, "y": 500, "w": 350, "h": 200},
      "player_1": {"x": 250, "y": 200, "w": 350, "h": 200}, 
      "player_2": {"x": 900, "y": 200, "w": 350, "h": 200}
    }
  }
}
```

---

## 📈 Performance Targets & Metrics

### Vision Performance KPIs
- **Card Detection Accuracy**: ≥99% for standard cards
- **Text Recognition Accuracy**: ≥98% for chip amounts and names  
- **Processing Latency**: ≤100ms per frame
- **False Positive Rate**: ≤1% for all detections
- **Frame Rate**: 30 FPS sustained (±1 FPS variance)

### System Performance KPIs  
- **Memory Usage**: ≤8GB total footprint
- **CPU Usage**: ≤60% sustained (Intel i5-8400)
- **GPU Usage**: ≤80% sustained (GTX 1080 Ti)
- **Storage Growth**: ~50MB per hour of play
- **Uptime**: ≥99% during active sessions

### Data Quality KPIs
- **Data Completeness**: ≥98% of game states captured
- **Timestamp Accuracy**: ±50ms precision
- **Database Integrity**: 0% corruption rate
- **Export Success**: 100% successful data exports

---

## 🧪 Testing Strategy

### Automated Tests
```python
# Example test cases
def test_card_detection():
    """Test card detection accuracy on known images"""
    assert detect_cards("test_images/royal_flush.jpg").accuracy > 0.99
    
def test_ocr_accuracy():
    """Test text recognition on chip amounts"""
    assert extract_pot_size("test_images/pot_500.jpg") == 500
    
def test_game_state_parsing():
    """Test complete game state reconstruction"""
    state = parse_game_state("test_images/flop_state.jpg")
    assert state.game_phase == "flop"
    assert len(state.community_cards) == 3
    
def test_database_operations():
    """Test data storage and retrieval"""
    game_state = create_test_game_state()
    save_game_state(game_state)
    retrieved = load_game_state(game_state.id)
    assert retrieved == game_state
```

### Manual Testing Scenarios
1. **Different Lighting Conditions**: Test under various screen brightness
2. **Card Variations**: Test with different card designs/themes
3. **UI Variations**: Test with different poker client versions
4. **Performance Stress**: Extended operation (8+ hours)
5. **Failure Recovery**: Simulate vision failures and recovery

---

## 🚀 Deployment & Distribution

### Installation Package Structure
```
poker_ai_mvp/
├── installer.exe              # Windows installer
├── src/                      # Application source code
├── models/                   # Pre-trained ML models
│   ├── yolov9_cards.pt      # Card detection model
│   └── ocr_model.onnx       # Text recognition model
├── config/
│   ├── settings.json        # Default configuration
│   └── regions.json         # Screen region definitions
├── data/                    # Data directory (created on first run)
├── logs/                    # Log directory (created on first run)
├── requirements.txt         # Python dependencies
└── README.md               # Setup instructions
```

### System Requirements Check
```python
def check_system_requirements():
    """Verify system meets minimum requirements"""
    checks = {
        "python_version": sys.version_info >= (3, 11),
        "ram_available": psutil.virtual_memory().total >= 16 * 1024**3,
        "gpu_available": torch.cuda.is_available(),
        "disk_space": shutil.disk_usage('.').free >= 100 * 1024**3,
        "screen_resolution": get_screen_resolution() >= (1920, 1080)
    }
    return all(checks.values()), checks
```

---

## 📋 MVP Acceptance Criteria

### Core Functionality ✅
- [ ] Real-time screen capture at 30 FPS
- [ ] Accurate card detection (>99% for standard conditions)
- [ ] OCR text recognition for all numeric values
- [ ] Complete game state reconstruction
- [ ] SQLite database storage with proper schema
- [ ] Real-time dashboard with live updates

### Data Quality ✅  
- [ ] All community cards detected and identified correctly
- [ ] Player stack sizes read accurately from UI
- [ ] Pot amounts captured with <1% error rate
- [ ] Timer countdown tracked precisely
- [ ] Hand phases identified correctly (preflop/flop/turn/river)

### Performance ✅
- [ ] Sustained 30 FPS processing without frame drops
- [ ] <100ms processing latency per frame
- [ ] <8GB total memory usage
- [ ] 8+ hours continuous operation without crashes
- [ ] Database operations complete within 10ms

### User Experience ✅
- [ ] One-click start/stop functionality
- [ ] Clear visual indicators for system status
- [ ] Real-time performance metrics display
- [ ] Export functionality for collected data
- [ ] Error notifications and recovery guidance

### Technical Quality ✅
- [ ] Comprehensive error handling and logging
- [ ] Graceful degradation when vision fails
- [ ] Proper database transaction handling
- [ ] Clean shutdown and resource cleanup
- [ ] Unit test coverage >80%

---

## 🎯 Success Criteria

**MVP is considered successful when:**

1. **Accuracy**: System maintains >98% detection accuracy for 1000+ consecutive hands
2. **Reliability**: Runs continuously for 8+ hours without manual intervention  
3. **Performance**: Processes frames at 30 FPS with <5% variance
4. **Data Quality**: Generates clean, structured data suitable for ML training
5. **Usability**: Non-technical user can start/stop system and export data

**Ready for Phase 2 when:**
- 10,000+ hands of high-quality training data collected
- Vision pipeline proven robust across different game conditions
- Database contains representative samples of all game scenarios
- Performance benchmarks consistently met over extended periods