"""Screen capture module for Poker AI MVP."""
import time
import threading
from datetime import datetime
from typing import Optional, Callable, Any
import numpy as np
import mss
from PIL import Image
import cv2
from loguru import logger

from ..config.settings import settings
from ..data.error_logger import log_capture_error, log_performance_issue, ErrorSeverity


class ScreenCapture:
    """High-performance screen capture for poker client."""
    
    def __init__(self):
        self.sct = None  # Initialize per thread
        self.running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_callback: Optional[Callable[[np.ndarray, datetime], None]] = None
        self.fps_target = settings.screen_capture.fps
        self.frame_interval = 1.0 / self.fps_target
        
        # Performance metrics
        self.frames_captured = 0
        self.last_fps_check = time.time()
        self.current_fps = 0.0
        self.error_count = 0
        self.consecutive_errors = 0
        
        # Screen region
        self.monitor = {
            "top": settings.screen_capture.region["y"],
            "left": settings.screen_capture.region["x"],
            "width": settings.screen_capture.region["width"],
            "height": settings.screen_capture.region["height"]
        }
        
        logger.info(f"ScreenCapture initialized - Region: {self.monitor}, Target FPS: {self.fps_target}")
    
    def set_frame_callback(self, callback: Callable[[np.ndarray, datetime], None]) -> None:
        """Set callback function for each captured frame."""
        self.frame_callback = callback
    
    def start_capture(self) -> None:
        """Start continuous screen capture."""
        if self.running:
            logger.warning("Screen capture already running")
            return
            
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("Screen capture started")
    
    def stop_capture(self) -> None:
        """Stop screen capture."""
        if not self.running:
            return
            
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
            
        # Cleanup MSS instance
        if self.sct:
            try:
                self.sct.close()
            except:
                pass
            self.sct = None
            
        logger.info("Screen capture stopped")
    
    def capture_single_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame."""
        try:
            # Initialize MSS instance if not exists (thread-safe)
            if self.sct is None:
                self.sct = mss.mss()
                
            # Capture screenshot
            screenshot = self.sct.grab(self.monitor)
            
            # Convert to PIL Image then numpy array
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            frame = np.array(img)
            
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Reset consecutive error count on success
            self.consecutive_errors = 0
            return frame
        except Exception as e:
            self.error_count += 1
            self.consecutive_errors += 1
            
            # Determine severity based on consecutive errors
            if self.consecutive_errors > 10:
                severity = ErrorSeverity.CRITICAL
            elif self.consecutive_errors > 5:
                severity = ErrorSeverity.HIGH
            else:
                severity = ErrorSeverity.MEDIUM
            
            # Log structured error with context
            log_capture_error(
                message=f"Screen capture failed: {str(e)}",
                exception=e,
                severity=severity,
                additional_data={
                    "monitor_region": self.monitor,
                    "consecutive_errors": self.consecutive_errors,
                    "total_errors": self.error_count,
                    "current_fps": self.current_fps,
                    "frames_captured": self.frames_captured
                }
            )
            
            logger.error(f"Failed to capture frame: {e}")
            return None
    
    def _capture_loop(self) -> None:
        """Main capture loop running in separate thread."""
        logger.info("Starting capture loop")
        
        while self.running:
            start_time = time.time()
            
            # Capture frame
            frame = self.capture_single_frame()
            if frame is None:
                continue
            
            # Call callback if set
            if self.frame_callback:
                try:
                    callback_start = time.time()
                    self.frame_callback(frame, datetime.now())
                    callback_time = (time.time() - callback_start) * 1000
                    
                    # Log performance issues if callback is slow
                    if callback_time > 50:  # More than 50ms
                        log_performance_issue(
                            message=f"Slow frame callback processing: {callback_time:.1f}ms",
                            severity=ErrorSeverity.MEDIUM if callback_time > 100 else ErrorSeverity.LOW,
                            additional_data={
                                "callback_time_ms": callback_time,
                                "target_frame_time_ms": self.frame_interval * 1000,
                                "current_fps": self.current_fps
                            }
                        )
                        
                except Exception as e:
                    log_capture_error(
                        message=f"Frame callback failed: {str(e)}",
                        exception=e,
                        severity=ErrorSeverity.HIGH,
                        additional_data={
                            "frames_captured": self.frames_captured,
                            "current_fps": self.current_fps
                        }
                    )
                    logger.error(f"Frame callback error: {e}")
            
            # Update performance metrics
            self.frames_captured += 1
            self._update_fps_metrics()
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, self.frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _update_fps_metrics(self) -> None:
        """Update FPS performance metrics."""
        current_time = time.time()
        if current_time - self.last_fps_check >= 1.0:  # Update every second
            elapsed = current_time - self.last_fps_check
            frames_in_period = self.frames_captured
            self.current_fps = frames_in_period / elapsed
            
            # Reset counters
            self.frames_captured = 0
            self.last_fps_check = current_time
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics."""
        return {
            "current_fps": round(self.current_fps, 1),
            "target_fps": self.fps_target,
            "frames_captured": self.frames_captured,
            "is_running": self.running,
            "total_errors": self.error_count,
            "consecutive_errors": self.consecutive_errors,
            "error_rate": self.error_count / max(1, self.frames_captured) if self.frames_captured > 0 else 0
        }
    
    def update_region(self, x: int, y: int, width: int, height: int) -> None:
        """Update capture region."""
        self.monitor = {
            "top": y,
            "left": x, 
            "width": width,
            "height": height
        }
        logger.info(f"Capture region updated: {self.monitor}")
    
    def save_frame(self, frame: np.ndarray, filename: str) -> bool:
        """Save frame to file for debugging."""
        try:
            cv2.imwrite(filename, frame)
            logger.info(f"Frame saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save frame: {e}")
            return False