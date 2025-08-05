"""Main application entry point for Poker AI MVP."""
import sys
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger

# Configure loguru
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/poker_ai_{time}.log", rotation="1 day", retention="7 days", level="DEBUG")

from .vision.capture import ScreenCapture
from .vision.state_parser import GameStateParser
from .data.database import DatabaseManager
from .data.logger import DataLogger
from .data.models import GameState, VisionMetrics
from .dashboard.main_window import MainDashboard
from .config.settings import settings


class PokerAIApplication:
    """Main application class for Poker AI MVP."""
    
    def __init__(self):
        # Core components
        self.screen_capture = ScreenCapture()
        self.state_parser = GameStateParser()
        self.database = DatabaseManager()
        
        # State
        self.is_running = False
        self.session_id: Optional[int] = None
        self.data_logger: Optional[DataLogger] = None
        self.current_game_state: Optional[GameState] = None
        self.processing_stats = {
            "frames_processed": 0,
            "frames_per_second": 0.0,
            "avg_processing_time": 0.0,
            "last_processing_time": 0,
            "errors_count": 0,
            "start_time": None
        }
        
        # GUI
        self.dashboard = MainDashboard()
        self._setup_dashboard_callbacks()
        
        # Debug tools
        self.window_detector = None
        self.vision_debugger = None
        
        logger.info("PokerAI application initialized")
    
    def _setup_dashboard_callbacks(self) -> None:
        """Setup callbacks between dashboard and application."""
        self.dashboard.set_start_callback(self.start_system)
        self.dashboard.set_stop_callback(self.stop_system)
        self.dashboard.set_export_callback(self.export_data)
        self.dashboard.set_settings_callback(self.show_settings)
        self.dashboard.set_debug_callback(self.launch_debug_tools)
        self.dashboard.set_calibrate_callback(self.launch_calibration)
        
        # Data callbacks
        self.dashboard.set_get_game_state_callback(self.get_current_game_state)
        self.dashboard.set_get_performance_stats_callback(self.get_performance_stats)
        self.dashboard.set_get_session_stats_callback(self.get_session_stats)
    
    def start_system(self) -> None:
        """Start the poker AI vision system."""
        try:
            if self.is_running:
                logger.warning("System already running")
                return
            
            logger.info("Starting poker AI system...")
            
            # Create new session
            self.session_id = self.database.create_session()
            self.dashboard.set_session_id(self.session_id)
            
            # Initialize data logger
            self.data_logger = DataLogger(self.session_id)
            
            # Setup screen capture callback
            self.screen_capture.set_frame_callback(self.process_frame)
            
            # Start screen capture
            self.screen_capture.start_capture()
            
            # Update state
            self.is_running = True
            self.processing_stats["start_time"] = datetime.now()
            
            # Log startup
            self.dashboard.add_activity("System started successfully")
            self.data_logger.log_event("system_start", {
                "session_id": self.session_id,
                "settings": settings.model_dump()
            })
            
            logger.info(f"System started - Session ID: {self.session_id}")
            
        except Exception as e:
            error_msg = f"Failed to start system: {str(e)}"
            logger.error(error_msg)
            self.dashboard.show_error("Startup Error", error_msg)
    
    def stop_system(self) -> None:
        """Stop the poker AI vision system."""
        try:
            if not self.is_running:
                logger.warning("System not running")
                return
            
            logger.info("Stopping poker AI system...")
            
            # Stop screen capture
            self.screen_capture.stop_capture()
            
            # Close data logger
            if self.data_logger:
                self.data_logger.log_event("system_stop", {
                    "frames_processed": self.processing_stats["frames_processed"],
                    "session_duration": (datetime.now() - self.processing_stats["start_time"]).total_seconds()
                })
                self.data_logger.close()
            
            # Update state
            self.is_running = False
            self.current_game_state = None
            
            # Log shutdown
            self.dashboard.add_activity("System stopped")
            
            logger.info("System stopped successfully")
            
        except Exception as e:
            error_msg = f"Error stopping system: {str(e)}"
            logger.error(error_msg)
            self.dashboard.show_error("Shutdown Error", error_msg)
    
    def process_frame(self, frame, timestamp: datetime) -> None:
        """Process captured frame."""
        if not self.is_running:
            return
        
        try:
            start_time = time.time()
            
            # Parse game state from frame
            game_state = self.state_parser.parse_game_state(frame, timestamp)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update stats
            self.processing_stats["frames_processed"] += 1
            self.processing_stats["last_processing_time"] = processing_time_ms
            
            # Calculate FPS
            if self.processing_stats["start_time"]:
                elapsed = (datetime.now() - self.processing_stats["start_time"]).total_seconds()
                if elapsed > 0:
                    self.processing_stats["frames_per_second"] = self.processing_stats["frames_processed"] / elapsed
            
            if game_state:
                # Store current game state
                self.current_game_state = game_state
                
                # Log to database
                if self.data_logger:
                    self.data_logger.log_game_state(game_state)
                
                # Calculate vision metrics
                vision_metrics = self.state_parser.calculate_vision_metrics(game_state, processing_time_ms)
                vision_metrics.frame_rate = self.screen_capture.current_fps
                
                # Log vision metrics
                if self.data_logger:
                    self.data_logger.log_vision_metrics(vision_metrics)
                
                # Debug logging (reduced frequency)
                if self.processing_stats["frames_processed"] % 30 == 0:  # Every 30 frames
                    logger.debug(f"Processed frame - Hand: {game_state.hand_id}, "
                               f"Phase: {game_state.game_phase.value}, "
                               f"Processing: {processing_time_ms}ms")
            
            else:
                # Log processing failure
                self.processing_stats["errors_count"] += 1
                
                if self.data_logger and self.processing_stats["errors_count"] % 10 == 0:  # Every 10 errors
                    self.data_logger.log_error("frame_processing", 
                                             "Failed to parse game state from frame")
                
        except Exception as e:
            self.processing_stats["errors_count"] += 1
            logger.error(f"Frame processing error: {e}")
            
            if self.data_logger:
                self.data_logger.log_error("frame_processing_exception", str(e))
    
    def get_current_game_state(self) -> Optional[Dict[str, Any]]:
        """Get current game state for dashboard."""
        if self.current_game_state:
            return self.current_game_state.to_dict()
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for dashboard."""
        game_state = self.current_game_state
        
        return {
            "frame_rate": self.screen_capture.current_fps,
            "processing_time_ms": self.processing_stats["last_processing_time"],
            "text_ocr_confidence": 0.9 if game_state and game_state.pot_size > 0 else 0.0,
            "community_cards_count": len(game_state.community_cards) if game_state else 0,
            "errors_last_hour": min(self.processing_stats["errors_count"], 999),
            "frames_processed": self.processing_stats["frames_processed"]
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for dashboard."""
        if not self.session_id:
            return {}
        
        try:
            return self.database.get_session_stats(self.session_id)
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {}
    
    def export_data(self) -> str:
        """Export session data."""
        try:
            if not self.session_id:
                raise ValueError("No active session")
            
            filename = self.database.export_session_data(self.session_id, "json")
            
            if self.data_logger:
                self.data_logger.log_event("data_export", {"filename": filename})
            
            return filename
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ""
    
    def show_settings(self) -> None:
        """Show settings dialog (placeholder)."""
        self.dashboard.show_info("Settings", 
                                "Settings dialog will be implemented in future version.\n\n"
                                "Current settings can be modified in:\n"
                                "config/settings.json")
    
    def launch_debug_tools(self) -> None:
        """Launch vision debugging tools."""
        try:
            from .vision.debug_tools import VisionDebugger
            
            if self.vision_debugger is None:
                self.vision_debugger = VisionDebugger()
            
            # Launch in separate thread to avoid blocking
            import threading
            debug_thread = threading.Thread(target=self.vision_debugger.launch_debugger, daemon=True)
            debug_thread.start()
            
            self.dashboard.add_activity("Debug tools launched")
            
        except Exception as e:
            logger.error(f"Failed to launch debug tools: {e}")
            self.dashboard.show_error("Debug Error", f"Failed to launch debug tools: {str(e)}")
    
    def launch_calibration(self) -> None:
        """Launch SAFE region calibration tool."""
        try:
            from .vision.safe_window_detector import SafeWindowDetector, SafeRegionCalibrator
            
            self.dashboard.add_activity("Starting SAFE calibration mode")
            
            # Create safe window detector
            safe_detector = SafeWindowDetector()
            
            # Select screen region (completely safe - just screenshots)
            target_region = safe_detector.select_screen_region_interactive()
            
            if target_region:
                # Launch safe region calibration
                calibrator = SafeRegionCalibrator(safe_detector)
                regions = calibrator.calibrate_regions()
                
                if regions:
                    # Update settings with new regions
                    settings.game_client.table_regions.update(regions)
                    settings.save_to_file("config/settings.json")
                    
                    self.dashboard.add_activity(f"SAFELY calibrated {len(regions)} regions")
                    self.dashboard.show_info("Safe Calibration Complete", 
                                           f"Successfully calibrated {len(regions)} regions using SAFE methods.\n"
                                           f"No window manipulation or injection used.\n"
                                           f"Settings saved to config/settings.json")
                else:
                    self.dashboard.add_activity("Safe calibration cancelled")
            else:
                self.dashboard.add_activity("Region selection cancelled")
                
        except Exception as e:
            logger.error(f"Safe calibration failed: {e}")
            self.dashboard.show_error("Calibration Error", f"Safe calibration failed: {str(e)}")
    
    def run(self) -> None:
        """Run the main application."""
        try:
            logger.info("Starting PokerAI MVP application")
            
            # Add startup message to dashboard
            self.dashboard.add_activity("Application initialized")
            self.dashboard.add_activity("Ready to start vision system")
            
            # Start GUI main loop
            self.dashboard.run()
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            # Cleanup
            if self.is_running:
                self.stop_system()
            logger.info("Application shutdown complete")


def main():
    """Main entry point."""
    try:
        app = PokerAIApplication()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()