# Poker AI Bot - Product Requirements Document v5

## 1. Project Overview

### Vision
Build a focused poker AI system for a 3-player online poker client that starts with comprehensive vision recognition and data collection, then progressively adds strategic decision-making capabilities.

### Core Objectives - Phase 1 (MVP)
- **Real-time Vision Recognition**: Detect and interpret all game elements from the poker client
- **Comprehensive Data Logging**: Capture all game states for analysis and training
- **Real-time Dashboard**: Monitor vision accuracy and game state detection
- **Training Data Collection**: Build datasets for future AI training

### Core Objectives - Phase 2+ (Future)
- **Strategic Decision Making**: AI-powered poker decisions
- **Human Behavior Simulation**: Natural timing and mouse movements
- **Automated Actions**: Execute decisions in the game client

### Target Game Client
**Based on screenshot analysis:**
- **Resolution**: 1920x1080 primary target
- **Layout**: Fixed 3-player table layout with green felt background
- **UI Elements**: Modern web-based poker interface with avatars and chip stacks
- **Card Style**: Standard playing cards with clear rank/suit visibility
- **Timer**: Visible countdown timer (01:35 format)
- **Betting**: Slider-based betting with percentage options (35%, 65%, Pot, All-in)

---

## 2. System Architecture

### High-Level Architecture (Simplified)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Vision Layer   │───▶│  Data Logger    │───▶│    Dashboard    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 SQLite Database                             │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture
- **Single Python Application**: Monolithic design for simplicity
- **Desktop UI**: tkinter-based dashboard for real-time monitoring
- **SQLite Database**: Local data storage for game states and metrics
- **File-based Logging**: Structured logs for debugging and analysis

---

## 3. Technical Stack (Simplified)

### 3.1 Vision & Recognition
| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Object Detection | YOLOv9 (ultralytics 8.2.0) | Detect cards, chips, buttons, avatars |
| Text Recognition | PaddleOCR 2.7.3 | Read stack sizes, bet amounts, timer |
| Card Recognition | Custom CNN (PyTorch 2.1.0) | Identify specific card ranks/suits |
| Screen Capture | mss 9.0.1 | Efficient desktop screenshots |
| Image Processing | OpenCV 4.8.1, Pillow 10.0.1 | Preprocessing and enhancement |

### 3.2 Core Application
| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Runtime | Python 3.11+ | Main application language |
| GUI Framework | tkinter (built-in) | Desktop dashboard interface |
| Database | SQLite 3 (built-in) | Local data storage |
| Async Processing | asyncio (built-in) | Real-time processing |
| Configuration | python-dotenv, Pydantic | Settings management |
| Logging | loguru 0.7.2 | Structured logging |

### 3.3 Data & Analytics
| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Data Processing | Pandas 2.1.1, NumPy 1.24.3 | Game data analysis |
| Visualization | Matplotlib 3.7.2 | Performance charts |
| Database ORM | SQLAlchemy 2.0.21 | Database operations |

### 3.4 Development Tools
| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Testing | pytest 7.4.2 | Unit and integration testing |
| Code Quality | Black, flake8, mypy | Code formatting and linting |
| Version Control | Git | Source code management |

---

## 4. Hardware Requirements

### Minimum Specifications
- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600 (6-core minimum for real-time processing)
- **GPU**: NVIDIA GTX 1080 Ti (11GB VRAM for YOLOv9 inference)
- **RAM**: 16GB DDR4 (8GB for OS/apps, 4GB for ML models, 4GB buffer)
- **Storage**: 100GB available space (50GB for datasets, 50GB for logs/data)
- **Display**: 1920x1080 primary monitor
- **OS**: Windows 11 Pro

### Performance Targets
- **Frame Rate**: 30 FPS screen capture sustained
- **Vision Processing**: <100ms per frame analysis
- **Memory Usage**: <8GB total application footprint
- **CPU Usage**: <60% sustained load
- **Storage Growth**: ~1GB per day of continuous play

---

## 5. Vision Pipeline Detailed

### 5.1 Game Element Detection
Based on the poker client screenshot, the system must detect:

**Player Information:**
- Player avatars and positions (3 fixed positions)
- Player names (chris48, Routine, xlv)
- Stack sizes (500, 460, 460 chips)
- Current action indicators

**Card Recognition:**
- Community cards (flop: 4♦, 10♥, 10♣)
- Player hole cards (Q♦, 4♥ visible for current player)
- Card positioning and orientation

**Game State Elements:**
- Pot size (80 chips)
- Current bet amounts
- Timer countdown (01:35 format)
- Betting round indicator ("DEUX PAIRES")

**UI Elements:**
- Action buttons (Fold, Check, Bet)
- Betting slider (35%, 65%, Pot, All-in)
- Bet amount input (20)

### 5.2 Processing Pipeline
```
Screen Capture (30 FPS) → 
Region of Interest Extraction → 
Parallel Processing:
├── Card Detection (YOLOv9)
├── Text Recognition (PaddleOCR)  
├── UI Element Detection
└── Game State Validation
→ Structured Data Output
```

### 5.3 Data Schema
```python
GameState = {
    "timestamp": datetime,
    "hand_id": str,
    "game_phase": ["preflop", "flop", "turn", "river"],
    "pot_size": int,
    "community_cards": List[Card],
    "players": List[Player],
    "current_player": int,
    "timer_remaining": int,
    "available_actions": List[str],
    "betting_options": Dict
}

Player = {
    "name": str,
    "position": int,
    "stack_size": int,
    "hole_cards": List[Card],
    "current_bet": int,
    "action": str
}

Card = {
    "rank": str,  # "A", "K", "Q", ..., "2"
    "suit": str,  # "♠", "♥", "♦", "♣"
    "confidence": float
}
```

---

## 6. Real-time Dashboard Specifications

### 6.1 Layout (tkinter Desktop App)
```
┌─────────────────────────────────────────────────────────┐
│ Poker AI Vision Monitor                    [●] Running  │
├─────────────────────────────────────────────────────────┤
│ ┌─── Live Game View ────┐  ┌─── Detection Stats ────┐  │
│ │ Current Hand: #1234   │  │ Cards Detected: 5/5    │  │
│ │ Phase: Flop           │  │ Text OCR: 98.5%        │  │
│ │ Pot: 80 chips         │  │ Players: 3/3           │  │
│ │ Timer: 01:35          │  │ Frame Rate: 30 FPS     │  │
│ └─────────────────────── │  └───────────────────────  │
│ ┌─── Players ───────────┐  ┌─── Logs ──────────────┐  │
│ │ chris48: 500 chips    │  │ [12:34] Hand started   │  │
│ │ Routine: 460 chips    │  │ [12:35] Cards detected │  │
│ │ xlv: 460 chips        │  │ [12:36] Bet placed     │  │
│ └─────────────────────── │  └───────────────────────  │
├─────────────────────────────────────────────────────────┤
│ [Start] [Stop] [Settings] [Export Data] [View Stats]   │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Key Metrics Display
- **Vision Accuracy**: Real-time confidence scores
- **Detection Count**: Cards/players/text successfully identified
- **Processing Speed**: FPS and latency metrics
- **Error Rates**: Failed detections per minute
- **Session Stats**: Hands logged, uptime, data collected

---

## 7. Data Pipeline & Storage

### 7.1 SQLite Database Schema
```sql
-- Game sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_hands INTEGER,
    status TEXT
);

-- Individual hands
CREATE TABLE hands (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    hand_number INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    final_pot INTEGER,
    winner TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

-- Game states (multiple per hand)
CREATE TABLE game_states (
    id INTEGER PRIMARY KEY,
    hand_id INTEGER,
    timestamp TIMESTAMP,
    game_phase TEXT,
    pot_size INTEGER,
    community_cards TEXT, -- JSON
    timer_remaining INTEGER,
    FOREIGN KEY (hand_id) REFERENCES hands (id)
);

-- Player states
CREATE TABLE player_states (
    id INTEGER PRIMARY KEY,
    game_state_id INTEGER,
    player_name TEXT,
    position INTEGER,
    stack_size INTEGER,
    hole_cards TEXT, -- JSON
    current_bet INTEGER,
    action TEXT,
    FOREIGN KEY (game_state_id) REFERENCES game_states (id)
);

-- Vision confidence metrics
CREATE TABLE vision_metrics (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP,
    card_detection_confidence REAL,
    text_ocr_confidence REAL,
    processing_time_ms INTEGER,
    frame_rate REAL
);
```

### 7.2 Real-time Processing
- **Capture Frequency**: 30 FPS continuous
- **Processing Queue**: Async processing to avoid frame drops
- **Data Retention**: Store all states for first 30 days, then sample
- **Export Formats**: JSON, CSV for external analysis

---

## 8. Performance Benchmarks

### 8.1 Vision Performance Targets
- **Card Detection Accuracy**: >99% for standard lighting
- **Text Recognition Accuracy**: >98% for stack sizes and pot amounts
- **Processing Latency**: <100ms from capture to data storage
- **Frame Rate**: 30 FPS sustained with <1% frame drops

### 8.2 System Performance Targets
- **Memory Usage**: <8GB total (4GB for models, 4GB for processing)
- **CPU Usage**: <60% sustained (i5-8400 baseline)
- **GPU Usage**: <80% (GTX 1080 Ti baseline)
- **Storage I/O**: <50MB/min continuous logging

### 8.3 Reliability Targets
- **Uptime**: >99% during active sessions
- **Data Integrity**: <0.1% corrupted frames
- **Recovery Time**: <5 seconds from vision failures
- **False Positive Rate**: <2% for card detection

---

## 9. Development Environment

### 9.1 Project Structure
```
poker_ai/
├── src/
│   ├── vision/
│   │   ├── capture.py          # Screen capture
│   │   ├── detection.py        # YOLO card detection
│   │   ├── ocr.py             # Text recognition
│   │   └── state_parser.py    # Game state extraction
│   ├── data/
│   │   ├── database.py        # SQLite operations
│   │   ├── logger.py          # Data logging
│   │   └── models.py          # Data models
│   ├── dashboard/
│   │   ├── main_window.py     # tkinter GUI
│   │   ├── widgets.py         # Custom UI components
│   │   └── charts.py          # Real-time charts
│   ├── config/
│   │   ├── settings.py        # Configuration
│   │   └── models/            # ML model files
│   └── main.py                # Application entry point
├── tests/
├── data/
│   ├── raw/                   # Training images
│   ├── processed/             # Preprocessed data
│   └── models/                # Trained models
├── logs/
├── requirements.txt
└── README.md
```

### 9.2 Setup Instructions
1. **Python Environment**: Python 3.11+ with venv
2. **Dependencies**: `pip install -r requirements.txt`
3. **GPU Setup**: CUDA 11.8+ for PyTorch
4. **Models**: Download YOLOv9 weights and card dataset
5. **Configuration**: Set screen resolution and game client path

---

## 10. Error Handling & Recovery

### 10.1 Vision Failure Scenarios
- **Partial Card Detection**: Log confidence scores, flag for review
- **OCR Failures**: Use previous known values with timestamp flags
- **Complete Vision Loss**: Alert user, pause data collection
- **False Detections**: Confidence thresholds and validation rules

### 10.2 System Recovery
- **Automatic Retry**: 3 attempts for transient failures
- **Graceful Degradation**: Continue with partial data
- **User Alerts**: Desktop notifications for critical failures
- **Data Recovery**: SQLite WAL mode for crash protection

---

## 11. Future Enhancements (Post-MVP)

### 11.1 Strategic AI (Phase 2)
- **Decision Engine**: GTO-based poker strategy
- **Opponent Modeling**: Basic player profiling
- **Action Execution**: Mouse/keyboard automation

### 11.2 Advanced Features (Phase 3+)
- **Multi-table Support**: Handle multiple game windows
- **Advanced Analytics**: Statistical analysis and reporting
- **Strategy Optimization**: Machine learning improvements
- **Tournament Support**: Different game formats

### 11.3 Game Rules Integration
- **No Limit Hold'em**: Standard betting rules
- **Blind Structure**: Automatic blind level detection
- **Side Pots**: Multi-player all-in scenarios
- **Tournament**: Progressive blind increases

---

## 12. Implementation Timeline

### Phase 1: MVP (Vision + Logging) - 6 weeks
**Week 1-2**: Core vision pipeline
- Screen capture implementation
- YOLOv9 integration for card detection
- Basic OCR for text recognition

**Week 3-4**: Data pipeline
- SQLite database setup
- Real-time data logging
- Basic error handling

**Week 5-6**: Dashboard and testing
- tkinter GUI implementation
- Real-time monitoring
- Testing and optimization

### Phase 2: Strategy Integration - 4 weeks
- Decision engine implementation
- Action execution system
- Human behavior simulation

### Phase 3: Advanced Features - Ongoing
- Multi-table support
- Advanced analytics
- Performance optimization

---

## 13. Success Metrics

### MVP Success Criteria
- **Vision Accuracy**: >98% card detection in controlled conditions
- **Data Completeness**: >95% of game states captured successfully
- **System Stability**: >8 hours continuous operation without crashes
- **Performance**: 30 FPS sustained processing
- **Usability**: One-click start/stop with clear status indicators

### Long-term Success Criteria
- **Win Rate**: 60% target (post-strategy implementation)
- **Detection Robustness**: Works across different lighting/screen conditions
- **Scalability**: Support for extended training sessions (days/weeks)
- **Data Quality**: Clean, structured data suitable for ML training

---

## 14. Risk Mitigation

### Technical Risks
- **Model Accuracy**: Extensive testing with diverse card images
- **Performance**: Optimize processing pipeline for real-time operation
- **Hardware Compatibility**: Test across different GPU configurations

### Data Risks
- **Privacy**: All data stored locally, no external transmission
- **Integrity**: Regular database backups and validation
- **Retention**: Clear data lifecycle and cleanup policies

### Operational Risks
- **User Experience**: Simple interface with clear status indicators
- **Maintenance**: Automated model updates and system health checks
- **Support**: Comprehensive logging for troubleshooting