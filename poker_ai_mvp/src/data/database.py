"""Database operations for Poker AI MVP."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from loguru import logger

from .models import GameState, Player, Card, VisionMetrics, SessionInfo
from ..config.settings import settings


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database.path
        self.db_dir = Path(self.db_path).parent
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    total_hands INTEGER DEFAULT 0,
                    total_frames_processed INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Hands table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    hand_number INTEGER,
                    hand_id TEXT UNIQUE,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    final_pot INTEGER,
                    winner_position INTEGER,
                    hand_strength TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Game states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hand_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    game_phase TEXT,
                    pot_size INTEGER,
                    community_cards TEXT,
                    timer_remaining INTEGER,
                    current_player_position INTEGER,
                    available_actions TEXT,
                    betting_options TEXT,
                    FOREIGN KEY (hand_id) REFERENCES hands (hand_id)
                )
            """)
            
            # Player states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_state_id INTEGER,
                    position INTEGER,
                    name TEXT,
                    stack_size INTEGER,
                    hole_cards TEXT,
                    current_bet INTEGER,
                    is_active BOOLEAN,
                    is_current BOOLEAN,
                    FOREIGN KEY (game_state_id) REFERENCES game_states (id)
                )
            """)
            
            # Vision metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vision_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_time_ms INTEGER,
                    frame_rate REAL,
                    card_detection_confidence REAL,
                    text_ocr_confidence REAL,
                    elements_detected INTEGER,
                    elements_failed INTEGER,
                    error_details TEXT
                )
            """)
            
            # Annotations table for training data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS annotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ground_truth TEXT,
                    model_prediction TEXT,
                    confidence_scores TEXT,
                    is_validated BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hands_session_id ON hands (session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_states_hand_id ON game_states (hand_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_states_timestamp ON game_states (timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vision_metrics_timestamp ON vision_metrics (timestamp)")
            
            conn.commit()
            logger.info("Database tables created/verified")
    
    def create_session(self) -> int:
        """Create new session and return session ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (start_time, status) 
                VALUES (?, 'active')
            """, (datetime.now(),))
            conn.commit()
            session_id = cursor.lastrowid
            logger.info(f"Created new session: {session_id}")
            return session_id
    
    def end_session(self, session_id: int) -> None:
        """End session and update statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count hands in this session
            cursor.execute("SELECT COUNT(*) FROM hands WHERE session_id = ?", (session_id,))
            total_hands = cursor.fetchone()[0]
            
            # Count frames processed (game states)
            cursor.execute("""
                SELECT COUNT(*) FROM game_states gs
                JOIN hands h ON gs.hand_id = h.hand_id
                WHERE h.session_id = ?
            """, (session_id,))
            total_frames = cursor.fetchone()[0]
            
            # Update session
            cursor.execute("""
                UPDATE sessions 
                SET end_time = ?, total_hands = ?, total_frames_processed = ?, status = 'completed'
                WHERE id = ?
            """, (datetime.now(), total_hands, total_frames, session_id))
            
            conn.commit()
            logger.info(f"Session {session_id} ended - {total_hands} hands, {total_frames} frames")
    
    def save_game_state(self, game_state: GameState, session_id: int) -> int:
        """Save complete game state to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if hand exists, create if not
            cursor.execute("SELECT id FROM hands WHERE hand_id = ?", (game_state.hand_id,))
            hand_row = cursor.fetchone()
            
            if not hand_row:
                # Create new hand record
                cursor.execute("""
                    INSERT INTO hands (session_id, hand_id, start_time, hand_number)
                    VALUES (?, ?, ?, ?)
                """, (session_id, game_state.hand_id, game_state.timestamp, self._get_next_hand_number(session_id)))
                conn.commit()
            
            # Find current player position
            current_player_pos = None
            for player in game_state.players:
                if player.is_current:
                    current_player_pos = player.position
                    break
            
            # Insert game state
            cursor.execute("""
                INSERT INTO game_states (
                    hand_id, timestamp, game_phase, pot_size, community_cards,
                    timer_remaining, current_player_position, available_actions, betting_options
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_state.hand_id,
                game_state.timestamp,
                game_state.game_phase.value,
                game_state.pot_size,
                json.dumps([card.to_dict() for card in game_state.community_cards]),
                game_state.timer_remaining,
                current_player_pos,
                json.dumps(game_state.available_actions),
                json.dumps(game_state.betting_options)
            ))
            
            game_state_id = cursor.lastrowid
            
            # Insert player states
            for player in game_state.players:
                cursor.execute("""
                    INSERT INTO player_states (
                        game_state_id, position, name, stack_size, hole_cards,
                        current_bet, is_active, is_current
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_state_id,
                    player.position,
                    player.name,
                    player.stack_size,
                    json.dumps([card.to_dict() for card in player.hole_cards]),
                    player.current_bet,
                    player.is_active,
                    player.is_current
                ))
            
            conn.commit()
            return game_state_id
    
    def save_vision_metrics(self, metrics: VisionMetrics) -> None:
        """Save vision processing metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vision_metrics (
                    timestamp, processing_time_ms, frame_rate,
                    card_detection_confidence, text_ocr_confidence,
                    elements_detected, elements_failed, error_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.processing_time_ms,
                metrics.frame_rate,
                metrics.card_detection_confidence,
                metrics.text_ocr_confidence,
                metrics.elements_detected,
                metrics.elements_failed,
                json.dumps(metrics.error_details)
            ))
            conn.commit()
    
    def _get_next_hand_number(self, session_id: int) -> int:
        """Get next hand number for session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(hand_number), 0) + 1 
                FROM hands WHERE session_id = ?
            """, (session_id,))
            return cursor.fetchone()[0]
    
    def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Get session statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic session info
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return {}
            
            # Count hands
            cursor.execute("SELECT COUNT(*) FROM hands WHERE session_id = ?", (session_id,))
            total_hands = cursor.fetchone()[0]
            
            # Count game states (frames)
            cursor.execute("""
                SELECT COUNT(*) FROM game_states gs
                JOIN hands h ON gs.hand_id = h.hand_id
                WHERE h.session_id = ?
            """, (session_id,))
            total_frames = cursor.fetchone()[0]
            
            # Recent vision metrics
            cursor.execute("""
                SELECT AVG(card_detection_confidence), AVG(text_ocr_confidence),
                       AVG(frame_rate), AVG(processing_time_ms), COUNT(*)
                FROM vision_metrics 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            metrics_row = cursor.fetchone()
            
            return {
                "session_id": session_id,
                "start_time": session_row["start_time"],
                "status": session_row["status"],
                "total_hands": total_hands,
                "total_frames": total_frames,
                "avg_card_confidence": metrics_row[0] or 0.0,
                "avg_ocr_confidence": metrics_row[1] or 0.0,
                "avg_frame_rate": metrics_row[2] or 0.0,
                "avg_processing_time": metrics_row[3] or 0.0,
                "recent_metrics_count": metrics_row[4] or 0
            }
    
    def get_recent_game_states(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent game states for dashboard display."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gs.*, h.hand_number
                FROM game_states gs
                JOIN hands h ON gs.hand_id = h.hand_id
                ORDER BY gs.timestamp DESC
                LIMIT ?
            """, (limit,))
            
            states = []
            for row in cursor.fetchall():
                state_dict = dict(row)
                # Parse JSON fields
                state_dict["community_cards"] = json.loads(row["community_cards"] or "[]")
                state_dict["available_actions"] = json.loads(row["available_actions"] or "[]")
                state_dict["betting_options"] = json.loads(row["betting_options"] or "{}")
                states.append(state_dict)
            
            return states
    
    def export_session_data(self, session_id: int, format: str = "json") -> str:
        """Export session data to file."""
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = export_dir / f"session_{session_id}_{timestamp}.{format}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all game states for session
            cursor.execute("""
                SELECT gs.*, h.hand_number, h.hand_id
                FROM game_states gs
                JOIN hands h ON gs.hand_id = h.hand_id
                WHERE h.session_id = ?
                ORDER BY gs.timestamp
            """, (session_id,))
            
            game_states = []
            for row in cursor.fetchall():
                state_dict = dict(row)
                state_dict["community_cards"] = json.loads(row["community_cards"] or "[]")
                state_dict["available_actions"] = json.loads(row["available_actions"] or "[]")
                state_dict["betting_options"] = json.loads(row["betting_options"] or "{}")
                
                # Get player states for this game state
                cursor.execute("""
                    SELECT * FROM player_states WHERE game_state_id = ?
                """, (row["id"],))
                
                players = []
                for player_row in cursor.fetchall():
                    player_dict = dict(player_row)
                    player_dict["hole_cards"] = json.loads(player_row["hole_cards"] or "[]")
                    players.append(player_dict)
                
                state_dict["players"] = players
                game_states.append(state_dict)
        
        # Export data
        if format == "json":
            with open(filename, "w") as f:
                json.dump({
                    "session_id": session_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_states": len(game_states),
                    "game_states": game_states
                }, f, indent=2, default=str)
        
        logger.info(f"Session data exported to {filename}")
        return str(filename)
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up data older than specified days."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old vision metrics
            cursor.execute("""
                DELETE FROM vision_metrics 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
            
            # Delete old game states and related data
            cursor.execute("""
                DELETE FROM player_states 
                WHERE game_state_id IN (
                    SELECT gs.id FROM game_states gs
                    JOIN hands h ON gs.hand_id = h.hand_id
                    JOIN sessions s ON h.session_id = s.id
                    WHERE s.start_time < datetime('now', '-{} days')
                )
            """.format(days))
            
            cursor.execute("""
                DELETE FROM game_states 
                WHERE hand_id IN (
                    SELECT h.hand_id FROM hands h
                    JOIN sessions s ON h.session_id = s.id
                    WHERE s.start_time < datetime('now', '-{} days')
                )
            """.format(days))
            
            cursor.execute("""
                DELETE FROM hands 
                WHERE session_id IN (
                    SELECT id FROM sessions 
                    WHERE start_time < datetime('now', '-{} days')
                )
            """.format(days))
            
            cursor.execute("""
                DELETE FROM sessions 
                WHERE start_time < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()
            logger.info(f"Cleaned up data older than {days} days")