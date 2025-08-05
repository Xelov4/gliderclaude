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

| Component | Technology | Purpose |
|-----------|------------|---------|
| Object Detection | YOLOv9 | Detect cards, buttons, bet amounts |
| Text Recognition | PaddleOCR | Read numerical values, player names |
| Card Recognition | Custom CNN | Identify specific card ranks/suits |
| Screen Capture | mss, pyautogui | Efficient desktop screenshots |
| Image Processing | OpenCV, PIL | Image preprocessing and enhancement |

### 3.2 Strategic Decision Engine
**Purpose**: Analyze game state and make optimal poker decisions

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core Strategy | Custom Transformer | Main decision-making model |
| Opponent Modeling | LSTM Networks | Learn opponent behavior patterns |
| Fallback Logic | Rule-based System | Handle edge cases and failures |
| ML Framework | PyTorch | Model training and inference |

### 3.3 Behavioral Simulation Layer
**Purpose**: Execute actions with human-like characteristics

| Component | Technology | Purpose |
|-----------|------------|---------|
| Mouse Movement | Bézier Curves | Natural mouse path generation |
| Timing Simulation | Gaussian Mixture Models | Realistic action delays |
| Behavior Patterns | Hidden Markov Models | Complex behavior sequences |
| Input Control | PyAutoGUI, pynput | Mouse and keyboard automation |

### 3.4 Core Application Framework
**Purpose**: Main application infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Python 3.11+ | Main application language |
| API Framework | FastAPI | Internal service communication |
| Configuration | Environment Variables | System configuration management |
| Process Management | asyncio | Concurrent task handling |

### 3.5 Data & Analytics Stack
**Purpose**: Store, process, and analyze game data

| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary Database | PostgreSQL | Structured game data storage |
| Time Series DB | InfluxDB | Performance metrics over time |
| Cache Layer | Redis | Real-time state management |
| Message Queue | RabbitMQ | Inter-component communication |
| Analytics | Custom Python | Game analysis and insights |

### 3.6 Dashboard & Visualization
**Purpose**: Web interface for monitoring and analysis

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React + TypeScript | User interface |
| Visualization | D3.js, Chart.js | Data visualization |
| Backend API | Node.js + Express | Dashboard backend services |
| Real-time Updates | WebSocket | Live data streaming |

### 3.7 Infrastructure & Operations
**Purpose**: System monitoring, deployment, and maintenance

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker + Docker Compose | Application packaging |
| Monitoring | Prometheus + Grafana | System health monitoring |
| Logging | ELK Stack | Centralized log management |
| Deployment | Windows 11 Native | Target environment |

## 4. Core Components Detailed

### 4.1 Vision Pipeline
```
Screen Capture → Preprocessing → Object Detection → OCR → 
Card Recognition → Game State Parsing → State Validation
```

**Key Capabilities**:
- Real-time screen capture with minimal latency
- Multi-table support and window detection
- Robust card and chip recognition
- Game phase detection (pre-flop, flop, turn, river)
- Player position and action detection

### 4.2 Decision Engine
```
Game State → Opponent Analysis → Strategy Selection → 
Action Calculation → Risk Assessment → Final Decision
```

**Key Capabilities**:
- GTO (Game Theory Optimal) strategy implementation
- Dynamic opponent modeling and exploitation
- Bankroll management integration
- Multi-table decision coordination
- Tilt detection and adjustment

### 4.3 Execution Engine
```
Decision → Timing Calculation → Path Planning → 
Action Simulation → Input Execution → Verification
```

**Key Capabilities**:
- Human-like mouse movement patterns
- Realistic thinking time simulation
- Anti-detection behavioral patterns
- Error handling and retry logic
- Action verification and correction

### 4.4 Data Pipeline
```
Raw Events → Processing → Enrichment → Storage → 
Analytics → Insights → Dashboard Updates
```

**Key Capabilities**:
- Real-time data processing
- Historical data analysis
- Performance metrics calculation
- Opponent profiling
- Strategy effectiveness tracking

## 5. Key Features

### 5.1 Automated Game Management
- **Game Detection**: Automatically detect when poker games start/end
- **Session Management**: Handle multiple gaming sessions
- **Error Recovery**: Automatic recovery from disconnections or errors
- **Resource Management**: Optimize CPU/memory usage during operation

### 5.2 Advanced Behavioral Simulation
- **Human Timing Patterns**: Variable response times based on decision complexity
- **Natural Mouse Movement**: Curved paths with acceleration/deceleration
- **Break Simulation**: Periodic breaks and session management
- **Tilt Simulation**: Occasional "human" mistakes to avoid detection

### 5.3 Comprehensive Analytics
- **Real-time Performance**: Live tracking of wins/losses and key metrics
- **Historical Analysis**: Long-term performance trends and patterns
- **Opponent Insights**: Detailed opponent behavior analysis
- **Strategy Evaluation**: A/B testing of different strategic approaches

### 5.4 Security & Anti-Detection
- **Process Isolation**: No injection into poker client processes
- **Behavioral Randomization**: Varied patterns to avoid detection
- **Hardware Simulation**: Emulate real hardware input characteristics
- **Stealth Mode**: Minimal system footprint and resource usage

## 6. Unaddressed Topics & Questions

### 6.1 Model Training & Data
**Questions**:
- How will you acquire training data for the custom CNN card recognition model? with a "model training mode", I will play manually the game while the app will acquire live feed. 
- What poker training datasets will be used for the strategic decision engine? do you have any suggestions ? 
- How will you handle the initial "cold start" problem for opponent modeling? I don't know, do you have a suggestion or a simple base ? 

**Suggestions**:
- Consider using synthetic card images for initial training
- Implement transfer learning from existing poker AI research : how ? 
- Create a simulation environment for initial model training : it will use the "model training mode" to do that

### 6.2 Performance & Scalability
**Questions**:
- What are the target frame rates for screen capture and processing? the highest possible - the main objective is performance and reliability
- How will the system handle multiple poker tables simultaneously? it will not, only one at a time, that will be a later update (you can create a new chapter listing the later updates)
- What are acceptable latency requirements for decision making? 2000ms to 5000ms

**Suggestions**:
- Implement GPU acceleration for vision processing : the computer has no gpu
- Design modular architecture for horizontal scaling : add to later update
- Set specific SLA targets (e.g., <500ms decision time) : please add more details for this question. 

### 6.3 Security & Legal Considerations
**Questions**:
- How will you ensure compliance with online poker platform terms of service? It is compliant
- What anti-detection measures beyond behavioral simulation are needed? anti injection processes, and please add more to that
- Are there legal considerations for automated poker playing in target jurisdictions? it is compliant

**Suggestions**:
- Implement comprehensive logging for audit purposes
- Research legal frameworks in target regions
- Consider implementing "human override" capabilities - yes please

### 6.4 Testing & Validation
**Questions**:
- How will you test the system without risking real money initially? i will risk it, it is a low fee, don't mind
- What metrics will determine if the AI is playing "well enough"? game winrate, hands winrate
- How will you validate that behavioral simulation is sufficiently human-like? i will be able to determine pauses time between hands and between games

**Suggestions**:
- Implement play-money testing environment : no
- Create automated testing suite for vision accuracy : later update
- Develop behavioral analysis tools to measure human-likeness : later update

### 6.5 Configuration & Customization
**Questions**:
- How customizable should the strategic engine be for different game types? initially we will only play one game type. 3 players table, no limit holdem, quick blind raise
- What configuration options should be exposed to users? most
- How will strategy updates and improvements be deployed? the user will be able to launch a historical analysis on the data collected and the app will autonomously update it's improvements

**Suggestions**:
- Implement strategy configuration files : yes please
- Create web interface for parameter tuning : yes please
- Design hot-swappable strategy modules : later update

### 6.6 Error Handling & Recovery
**Questions**:
- How should the system handle partial game state recognition failures? try to pick any hint of the current game to keep up
- What happens when the poker client updates and changes its interface? later update
- How will network disconnections and reconnections be managed? later update

**Suggestions**:
- Implement graceful degradation for vision failures : later update
- Design adaptive UI element detection : later upate
- Create robust session state recovery mechanisms : later update

### 6.7 Monitoring & Observability
**Questions**:
- What key metrics should be monitored in real-time? cards in hand, flop etc, stacks
- How will you detect when the AI is making suboptimal decisions? later update
- What alerts should be implemented for system health? later update

**Suggestions**:
- Implement real-time performance dashboards : yes
- Create automated anomaly detection : yes
- Design comprehensive alerting system : yes

### 6.8 Deployment & Updates
**Questions**:
- How will model updates be deployed without interrupting active games? later update
- What rollback procedures are needed if updates cause issues? later update
- How will you handle different poker client versions? there will be only one

**Suggestions**:
- Implement blue-green deployment strategy : later update
- Create automated rollback mechanisms : later update
- Design version compatibility matrix : later update