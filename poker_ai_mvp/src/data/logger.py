"""Data logging and event tracking."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger as log_handler

from .models import GameState, VisionMetrics
from .database import DatabaseManager


class DataLogger:
    """Handles all data logging operations."""
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.db = DatabaseManager()
        
        # File logging setup
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create session-specific log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_dir / f"session_{session_id}_{timestamp}.jsonl"
        
        # Performance tracking
        self.frames_logged = 0
        self.last_hand_id = None
        self.events_buffer = []
        
        log_handler.info(f"DataLogger initialized for session {session_id}")
    
    def log_game_state(self, game_state: GameState) -> None:
        """Log complete game state."""
        try:
            # Save to database
            game_state_id = self.db.save_game_state(game_state, self.session_id)
            
            # Log to file
            self._log_to_file("game_state", {
                "game_state_id": game_state_id,
                "data": game_state.to_dict()
            })
            
            # Track hand transitions
            if game_state.hand_id != self.last_hand_id:
                self._log_hand_transition(game_state)
                self.last_hand_id = game_state.hand_id
            
            self.frames_logged += 1
            
        except Exception as e:
            log_handler.error(f"Failed to log game state: {e}")
    
    def log_vision_metrics(self, metrics: VisionMetrics) -> None:
        """Log vision processing metrics."""
        try:
            # Save to database
            self.db.save_vision_metrics(metrics)
            
            # Log to file
            self._log_to_file("vision_metrics", metrics.to_dict())
            
        except Exception as e:
            log_handler.error(f"Failed to log vision metrics: {e}")
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log custom event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data
        }
        
        self._log_to_file("event", event)
        self.events_buffer.append(event)
        
        # Keep buffer size manageable
        if len(self.events_buffer) > 1000:
            self.events_buffer = self.events_buffer[-500:]
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error with context."""
        error_data = {
            "error_type": error_type,
            "message": error_message,
            "context": context or {}
        }
        
        self.log_event("error", error_data)
        log_handler.error(f"{error_type}: {error_message}")
    
    def log_performance_milestone(self, milestone: str, metrics: Dict[str, Any]) -> None:
        """Log performance milestone."""
        milestone_data = {
            "milestone": milestone,
            "metrics": metrics,
            "frames_logged": self.frames_logged
        }
        
        self.log_event("performance_milestone", milestone_data)
        log_handler.info(f"Performance milestone: {milestone}")
    
    def _log_hand_transition(self, game_state: GameState) -> None:
        """Log new hand start."""
        hand_data = {
            "hand_id": game_state.hand_id,
            "game_phase": game_state.game_phase.value,
            "players": [p.name for p in game_state.players],
            "pot_size": game_state.pot_size
        }
        
        self.log_event("hand_start", hand_data)
        log_handler.info(f"New hand started: {game_state.hand_id}")
    
    def _log_to_file(self, log_type: str, data: Dict[str, Any]) -> None:
        """Log data to JSONL file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": log_type,
            "data": data
        }
        
        try:
            with open(self.session_log_file, "a") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")
        except Exception as e:
            log_handler.error(f"Failed to write to log file: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session logging summary."""
        return {
            "session_id": self.session_id,
            "frames_logged": self.frames_logged,
            "events_count": len(self.events_buffer),
            "log_file": str(self.session_log_file),
            "last_hand_id": self.last_hand_id
        }
    
    def export_session_logs(self, format: str = "json") -> str:
        """Export session logs to file."""
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"logs_session_{self.session_id}_{timestamp}.{format}"
        
        try:
            if format == "json":
                # Export as structured JSON
                export_data = {
                    "session_id": self.session_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "summary": self.get_session_summary(),
                    "events": self.events_buffer
                }
                
                with open(export_file, "w") as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            elif format == "csv":
                # Export events as CSV
                import csv
                
                with open(export_file, "w", newline="") as csvfile:
                    if self.events_buffer:
                        # Flatten event data for CSV
                        fieldnames = ["timestamp", "event_type"]
                        
                        # Find all unique data keys
                        data_keys = set()
                        for event in self.events_buffer:
                            if "data" in event and isinstance(event["data"], dict):
                                data_keys.update(event["data"].keys())
                        
                        fieldnames.extend(sorted(data_keys))
                        
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for event in self.events_buffer:
                            row = {
                                "timestamp": event["timestamp"],
                                "event_type": event["event_type"]
                            }
                            
                            if "data" in event and isinstance(event["data"], dict):
                                for key, value in event["data"].items():
                                    row[key] = str(value) if value is not None else ""
                            
                            writer.writerow(row)
            
            log_handler.info(f"Session logs exported to {export_file}")
            return str(export_file)
            
        except Exception as e:
            log_handler.error(f"Failed to export session logs: {e}")
            return ""
    
    def close(self) -> None:
        """Close logger and flush remaining data."""
        try:
            # Log session end
            self.log_event("session_end", {
                "frames_logged": self.frames_logged,
                "total_events": len(self.events_buffer)
            })
            
            # End database session
            self.db.end_session(self.session_id)
            
            log_handler.info(f"DataLogger closed for session {self.session_id}")
            
        except Exception as e:
            log_handler.error(f"Error closing DataLogger: {e}")


class ActivityLogger:
    """Logs user activity and system events."""
    
    def __init__(self):
        self.activities = []
        self.max_activities = 1000
    
    def log_activity(self, message: str, level: str = "info") -> None:
        """Log activity with timestamp."""
        activity = {
            "timestamp": datetime.now(),
            "message": message,
            "level": level
        }
        
        self.activities.append(activity)
        
        # Keep list manageable
        if len(self.activities) > self.max_activities:
            self.activities = self.activities[-500:]
        
        # Also log to loguru
        if level == "error":
            log_handler.error(message)
        elif level == "warning":
            log_handler.warning(message)
        else:
            log_handler.info(message)
    
    def get_recent_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent activities for dashboard display."""
        recent = self.activities[-limit:] if limit < len(self.activities) else self.activities
        
        return [{
            "timestamp": activity["timestamp"].strftime("%H:%M:%S"),
            "message": activity["message"],
            "level": activity["level"]
        } for activity in reversed(recent)]
    
    def clear_activities(self) -> None:
        """Clear activity log."""
        self.activities.clear()
        self.log_activity("Activity log cleared")