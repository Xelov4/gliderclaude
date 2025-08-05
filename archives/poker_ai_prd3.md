# Poker AI Bot - Product Requirements Document

## 1. Project Overview

### Vision
Build an autonomous poker playing system that combines computer vision, strategic AI, and human behavior simulation to play online poker games while maintaining undetectable, human-like behavior patterns.

### Core Objectives
- **Real-time Game Recognition**: Detect and interpret poker game states from desktop screenshots
- **Strategic Decision Making**: Make optimal poker decisions based on game state and opponent analysis
- **Human Behavior Emulation**: Execute actions with realistic timing, mouse movements, and behavioral patterns
- **Comprehensive Logging**: Capture all game data for performance analysis and strategy improvement
- **Performance Analytics**: Provide detailed insights through a web-based dashboard
- **Autonomous Operation**: Handle game lifecycle management (start, detect end, restart)

### Initial Scope
- **Single Table Focus**: One poker table at a time
- **Specific Game Type**: 3-player No Limit Hold'em with quick blind raise
- **Single Client**: Support for one specific poker client version
- **CPU-Only Processing**: No GPU acceleration required

## 2. System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Vision Layer   │───▶│ Decision Layer  │───▶│ Execution Layer │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Pipeline  │◀───┤ Analytics Engine│◀───┤  Event Logger   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard Interface                      │
└─────────────────────────────────────────────────────────────┘
```

### Core Processing Pipeline
1. **Screen Capture** → **Vision Processing** → **Game State Extraction**
2. **Strategic Analysis** → **Decision Making** → **Action Planning**
3. **Behavior Simulation** → **Input Execution** → **Action Logging**
4. **Data Processing** → **Analytics** → **Dashboard Updates**

## 3. Technical Stack

### 3.1 Vision & Recognition Layer
**Purpose**: Capture and interpret visual game information

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Object Detection | YOLOv9 (ultralytics 8.2.0) | Detect cards, buttons, bet amounts |
| Text Recognition | PaddleOCR 2.7.3 | Read numerical values, player names |
| Card Recognition | Custom CNN (PyTorch 2.1.0) | Identify specific card ranks/suits |
| Screen Capture | mss 9.0.1, pyautogui 0.9.54 | Efficient desktop screenshots |
| Image Processing | OpenCV 4.8.1, Pillow 10.0.1 | Image preprocessing and enhancement |
| ML Framework | PyTorch 2.1.0 + torchvision 0.16.0 | Model training and inference |

### 3.2 Strategic Decision Engine
**Purpose**: Analyze game state and make optimal poker decisions

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Core Strategy | Custom Transformer (PyTorch 2.1.0) | Main decision-making model |
| Opponent Modeling | LSTM Networks (PyTorch 2.1.0) | Learn opponent behavior patterns |
| Fallback Logic | Rule-based System (Python) | Handle edge cases and failures |
| Poker Logic | python-poker 0.1.4 | Hand evaluation and rankings |
| Data Science | NumPy 1.24.3, SciPy 1.11.3 | Mathematical computations |

### 3.3 Behavioral Simulation Layer
**Purpose**: Execute actions with human-like characteristics

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Mouse Movement | Bézier Curves (NumPy) | Natural mouse path generation |
| Timing Simulation | Gaussian Mixture (scikit-learn 1.3.0) | Realistic action delays |
| Behavior Patterns | Hidden Markov Models (hmmlearn 0.3.0) | Complex behavior sequences |
| Input Control | PyAutoGUI 0.9.54, pynput 1.7.6 | Mouse and keyboard automation |
| Randomization | Random, NumPy.random | Behavioral variance |

### 3.4 Core Application Framework
**Purpose**: Main application infrastructure

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Runtime | Python 3.11.5 | Main application language |
| API Framework | FastAPI 0.104.1 | Internal service communication |
| Async Processing | asyncio (built-in) | Concurrent task handling |
| Configuration | python-dotenv 1.0.0, Pydantic 2.4.2 | Environment and config management |
| Scheduling | APScheduler 3.10.4 | Task scheduling and automation |
| Logging | loguru 0.7.2 | Enhanced logging capabilities |

### 3.5 Data & Analytics Stack
**Purpose**: Store, process, and analyze game data

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Primary Database | PostgreSQL 15.4 + psycopg2 2.9.7 | Structured game data storage |
| Time Series DB | InfluxDB 2.7.3 + influxdb-client 1.38.0 | Performance metrics over time |
| Cache Layer | Redis 7.2.0 + redis-py 5.0.1 | Real-time state management |
| Message Queue | RabbitMQ 3.12.4 + pika 1.3.2 | Inter-component communication |
| Analytics | Pandas 2.1.1, Matplotlib 3.7.2 | Game analysis and insights |
| Data Processing | SQLAlchemy 2.0.21 | Database ORM |

### 3.6 Dashboard & Visualization
**Purpose**: Web interface for monitoring and analysis

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Frontend | React 18.2.0 + TypeScript 5.2.2 | User interface |
| UI Framework | Material-UI 5.14.10 | Component library |
| Visualization | D3.js 7.8.5, Chart.js 4.4.0 | Data visualization |
| State Management | Redux Toolkit 1.9.7 | Frontend state management |
| Backend API | Node.js 18.17.1 + Express 4.18.2 | Dashboard backend services |
| Real-time Updates | Socket.io 4.7.2 | Live data streaming |
| HTTP Client | Axios 1.5.0 | API communication |

### 3.7 Infrastructure & Operations
**Purpose**: System monitoring, deployment, and maintenance

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Containerization | Docker 24.0.6 + Docker Compose 2.21.0 | Application packaging |
| Monitoring | Prometheus 2.47.0 + Grafana 10.1.0 | System health monitoring |
| Logging | ELK Stack (Elasticsearch 8.9.0, Logstash 8.9.0, Kibana 8.9.0) | Centralized log management |
| Process Management | supervisord 4.2.5 | Service management |
| Environment | Windows 11 Pro | Target operating system |

### 3.8 Development & Testing Tools

| Component | Technology & Version | Purpose |
|-----------|---------------------|---------|
| Code Quality | Black 23.7.0, flake8 6.0.0, mypy 1.5.1 | Code formatting and linting |
| Testing | pytest 7.4.2, pytest-asyncio 0.21.1 | Unit and integration testing |
| Documentation | Sphinx 7.1.2 | Code documentation |
| Version Control | Git 2.42.0 | Source code management |
| IDE | VS Code 1.82.0 | Development environment |

## 4. Core Components Detailed

### 4.1 Vision Pipeline
```
Screen Capture → Preprocessing → Object Detection → OCR → 
Card Recognition → Game State Parsing → State Validation
```

**Key Capabilities**:
- High-frequency screen capture optimized for CPU processing
- Robust card and chip recognition for 3-player tables
- Game phase detection (pre-flop, flop, turn, river)
- Player position and action detection
- Stack size and bet amount recognition

**Performance Requirements**:
- Maximum frame rate for screen capture
- Decision latency: 2000-5000ms acceptable range
- CPU-optimized processing pipeline

### 4.2 Decision Engine
```
Game State → Opponent Analysis → Strategy Selection → 
Action Calculation → Risk Assessment → Final Decision
```

**Key Capabilities**:
- GTO (Game Theory Optimal) strategy for 3-player NLHE
- Basic opponent modeling with cold-start handling
- Bankroll management integration
- Quick blind raise adaptation

**Decision Timeline**:
- Game state analysis: <500ms
- Strategic calculation: <1500ms
- Final decision output: <2000ms total

### 4.3 Execution Engine
```
Decision → Timing Calculation → Path Planning → 
Action Simulation → Input Execution → Verification
```

**Key Capabilities**:
- Human-like mouse movement with Bézier curves
- Realistic thinking time (2-5 seconds)
- Anti-detection behavioral patterns
- Configurable pause timing between hands/games

### 4.4 Data Pipeline
```
Raw Events → Processing → Enrichment → Storage → 
Analytics → Insights → Dashboard Updates
```

**Key Capabilities**:
- Real-time data processing and storage
- Hand history logging and analysis
- Win rate and performance tracking
- Automated strategy improvement based on historical data

## 5. Key Features

### 5.1 Model Training Mode
- **Live Data Collection**: Capture training data while playing manually
- **Card Recognition Training**: Build custom dataset of card images
- **Behavioral Pattern Learning**: Record human timing and movement patterns
- **Strategy Validation**: Compare manual vs automated decisions

### 5.2 Advanced Behavioral Simulation
- **Variable Response Times**: 2-5 second decision windows with realistic variance
- **Natural Mouse Movement**: Curved paths with human-like acceleration
- **Configurable Breaks**: User-defined pause patterns between hands and games
- **Anti-Detection**: No process injection, hardware-level input simulation

### 5.3 Comprehensive Analytics Dashboard
- **Real-time Monitoring**: Live tracking of cards, stacks, and game state
- **Performance Metrics**: Game win rate and hand win rate tracking
- **Historical Analysis**: Long-term performance trends
- **Strategy Optimization**: Automated improvements based on collected data

### 5.4 Configuration & Customization
- **Strategy Parameters**: Extensive configuration options via web interface
- **Behavioral Settings**: Adjustable timing and movement patterns
- **Risk Management**: Bankroll and betting limits
- **Human Override**: Manual intervention capabilities

## 6. Detailed Requirements & Specifications

### 6.1 Model Training & Data Strategy

**Training Data Acquisition**:
- **Manual Training Mode**: Live data collection during manual play sessions
- **Card Recognition Dataset**: Build custom dataset with game-specific card images
- **Behavioral Data**: Record human timing patterns and mouse movements

**Strategic Decision Training**:
- **Public Datasets**: Utilize available poker hand databases (IRC Poker Database, PokerStars Hand Histories)
- **Transfer Learning**: Leverage existing poker AI research (Libratus, Pluribus papers)
- **Simulation Environment**: Use manual training mode data for initial model validation

**Cold Start Problem Solutions**:
- **Default Opponent Models**: Start with basic tight-aggressive opponent assumptions
- **Quick Adaptation**: Implement fast-learning algorithms for rapid opponent profiling
- **Fallback Strategies**: Rule-based decisions when opponent data is insufficient

### 6.2 Performance & Reliability Requirements

**System Performance**:
- **Frame Rate**: Maximum achievable on CPU-only processing
- **Decision Latency**: 2000-5000ms acceptable range
- **Reliability Target**: 99.5% uptime during gaming sessions
- **Memory Usage**: <4GB RAM allocation
- **CPU Usage**: <80% sustained load

**Quality Metrics**:
- **Vision Accuracy**: >98% card recognition accuracy
- **Decision Quality**: Measured against GTO benchmarks
- **Behavioral Authenticity**: User validation of timing patterns

### 6.3 Security & Anti-Detection Measures

**Core Security Principles**:
- **No Process Injection**: Pure screen capture and input simulation
- **Hardware-Level Simulation**: Authentic mouse and keyboard events
- **Behavioral Randomization**: Variable timing and movement patterns
- **Process Isolation**: Minimal system footprint

**Anti-Detection Features**:
- **Human Timing Variance**: Realistic decision time distribution
- **Mouse Movement Patterns**: Natural Bézier curve trajectories
- **Break Simulation**: Configurable pauses between hands and sessions
- **Error Simulation**: Occasional "human" mistakes and corrections

**Compliance Features**:
- **Comprehensive Logging**: Full audit trail for all actions
- **Human Override System**: Manual intervention capabilities
- **Transparent Operation**: No hidden or obfuscated functionality

### 6.4 Testing & Validation Strategy

**Testing Approach**:
- **Live Testing**: Direct deployment with low-stakes games
- **Performance Metrics**: Focus on game win rate and hand win rate
- **Behavioral Validation**: User assessment of pause timing authenticity

**Success Criteria**:
- **Win Rate**: Positive ROI over 1000+ hands
- **Behavioral Authenticity**: Undetectable operation patterns
- **System Stability**: <1% crash rate during sessions

### 6.5 Configuration & Customization Framework

**Game Type Support**:
- **Initial Focus**: 3-player No Limit Hold'em with quick blind raise
- **Table Limits**: Configurable stake levels
- **Session Management**: Automated start/stop with break scheduling

**User Configuration Options**:
- **Strategic Parameters**: Aggression levels, risk tolerance, bankroll management
- **Behavioral Settings**: Timing variance, movement patterns, break frequency
- **Monitoring Preferences**: Dashboard layout, alert thresholds, reporting frequency

**Strategy Updates**:
- **Automated Analysis**: Historical data processing for strategy improvements
- **Configuration Files**: JSON-based strategy parameter management
- **Web Interface**: Real-time parameter adjustment capabilities

### 6.6 Error Handling & Recovery

**Vision Failure Handling**:
- **Partial Recognition**: Continue operation with incomplete game state information
- **State Reconstruction**: Use previous game states and logical inference
- **Fallback Actions**: Conservative play when vision confidence is low
- **Manual Intervention**: Alert user for complex failure scenarios

**Recovery Mechanisms**:
- **Session State Persistence**: Maintain game state across minor failures
- **Automatic Retry**: Intelligent retry logic for transient failures
- **Graceful Degradation**: Reduced functionality rather than complete failure

### 6.7 Monitoring & Observability

**Real-time Monitoring**:
- **Game State**: Current cards, community cards, stack sizes, pot size
- **System Health**: CPU usage, memory consumption, processing latency
- **Performance Metrics**: Win rate, hand count, session duration

**Dashboard Features**:
- **Live Game View**: Real-time visualization of current game state
- **Performance Charts**: Historical win rate and profit/loss tracking
- **System Alerts**: Automated notifications for critical events
- **Anomaly Detection**: Identification of unusual patterns or behaviors

**Alerting System**:
- **Critical Alerts**: System failures, security concerns, significant losses
- **Performance Alerts**: Below-threshold win rates, unusual opponent behavior
- **Informational Alerts**: Session milestones, strategy updates

## 7. Core Implementation Features

### 7.1 Data Privacy & Storage
**Local Data Storage**: All sensitive game data stored locally on the user's machine, ensuring complete privacy and control over poker hand histories, strategic data, and behavioral patterns.

### 7.2 Real-time Dashboard Updates
**Sub-second Latency**: Critical game information updates on the dashboard with sub-second latency, providing immediate visibility into current game state, stack changes, and decision-making processes.

### 7.3 Automated Model Updates
**Self-improving Algorithms**: The system continuously analyzes collected historical data to identify strategic improvements and automatically updates decision-making models based on performance patterns and opponent behavior analysis.

### 7.4 Automated Data Backup
**Daily Incremental Backups**: Automatic daily backups of all critical data including hand histories, strategic configurations, opponent models, and performance analytics to prevent data loss and enable recovery.

## 8. Future Enhancements (Later Updates)

### 8.1 Multi-Table Support
- **Concurrent Processing**: Handle multiple poker tables simultaneously
- **Resource Management**: Distributed processing across tables
- **Decision Coordination**: Manage bankroll across multiple games

### 8.2 Advanced Security & Privacy
- **Data Encryption**: Encrypted storage for hand histories and strategy data
- **Data Retention Policies**: Configurable retention policies for historical data
- **Advanced Backup Strategy**: User-controlled backup scheduling with encryption

### 8.3 Enhanced User Experience
- **Responsive Design**: Dashboard compatibility across desktop and mobile devices
- **Customizable Layout**: User-configurable dashboard components and layouts
- **Accessibility Features**: Full keyboard navigation and screen reader support

### 8.4 Advanced Testing & Validation
- **Automated Vision Testing**: Comprehensive accuracy testing suite
- **Behavioral Analysis Tools**: Quantitative human-likeness measurement
- **A/B Strategy Testing**: Automated strategy comparison frameworks

### 8.5 Enhanced Configurability
- **Hot-Swappable Strategies**: Runtime strategy module updates
- **Multi-Game Support**: Different poker variants and table sizes
- **Advanced Opponent Modeling**: Sophisticated player profiling systems

### 8.6 Robustness & Adaptability
- **UI Change Detection**: Automatic adaptation to client updates
- **Network Resilience**: Advanced connection failure handling
- **Graceful Vision Degradation**: Intelligent handling of partial vision failures

### 8.7 Advanced Analytics & Monitoring
- **Configuration Versioning**: Track and rollback configuration changes
- **Component Updates**: Individual component updates without full system restart
- **Health Monitoring**: Proactive identification of performance degradation
- **Suboptimal Decision Detection**: Automated strategy quality assessment
- **Advanced Anomaly Detection**: Machine learning-based pattern recognition
- **Comprehensive Alerting**: Multi-channel notification system

### 8.8 Advanced Recovery & Maintenance
- **Recovery Procedures**: Documented recovery processes for all failure scenarios
- **Data Validation**: Integrity checks for all stored data
- **Disaster Recovery**: Complete system restoration from backup procedures

### 8.9 Deployment & Operations Enhancements
- **Blue-Green Deployments**: Zero-downtime update mechanisms
- **Automated Rollbacks**: Intelligent failure detection and recovery
- **Multi-Client Support**: Compatibility matrix for different poker clients

## 9. Implementation Roadmap

### Phase 1: Core Vision & Recognition (Months 1-2)
- Screen capture optimization
- Basic card and game state recognition
- Manual training mode implementation
- Initial dataset collection

### Phase 2: Strategic Decision Engine (Months 2-3)
- GTO strategy implementation for 3-player NLHE
- Basic opponent modeling
- Rule-based fallback system
- Decision pipeline optimization

### Phase 3: Behavioral Simulation (Months 3-4)
- Human-like mouse movement implementation
- Timing variance and behavioral patterns
- Anti-detection measures
- Input simulation system

### Phase 4: Data Pipeline & Analytics (Months 4-5)
- Database design and implementation
- Real-time data processing
- Basic dashboard development
- Performance metrics tracking

### Phase 5: Integration & Testing (Months 5-6)
- Full system integration
- Live testing and validation
- Performance optimization
- Bug fixes and stability improvements

### Phase 6: Advanced Features (Months 6-7)
- Automated model updates
- Advanced analytics dashboard
- Configuration management
- Human override system

### Phase 7: Production Deployment (Month 7)
- Final testing and validation
- Documentation completion
- Production deployment
- Monitoring and maintenance setup