"""Main dashboard window for Poker AI MVP."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from .widgets import (StatusIndicator, MetricsDisplay, GameStateDisplay,
                     PlayersDisplay, ActivityLog, ProgressChart)
from ..data.logger import ActivityLogger


class MainDashboard:
    """Main dashboard window for monitoring poker AI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker AI Vision Monitor v1.0")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # State
        self.is_running = False
        self.session_id = None
        self.update_thread = None
        self.stop_update_thread = False
        
        # Activity logger
        self.activity_logger = ActivityLogger()
        
        # Callbacks (set by main application)
        self.start_callback: Optional[Callable[[], None]] = None
        self.stop_callback: Optional[Callable[[], None]] = None
        self.export_callback: Optional[Callable[[], str]] = None
        self.settings_callback: Optional[Callable[[], None]] = None
        self.debug_callback: Optional[Callable[[], None]] = None
        self.calibrate_callback: Optional[Callable[[], None]] = None
        
        # Data update callbacks
        self.get_game_state_callback: Optional[Callable[[], Optional[Dict[str, Any]]]] = None
        self.get_performance_stats_callback: Optional[Callable[[], Dict[str, Any]]] = None
        self.get_session_stats_callback: Optional[Callable[[], Dict[str, Any]]] = None
        
        self._create_widgets()
        self._setup_layout()
        self._start_update_thread()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _create_widgets(self) -> None:
        """Create all dashboard widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title bar with status
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(self.title_frame, text="Poker AI Vision Monitor v1.0", 
                              font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.status_indicator = StatusIndicator(self.title_frame, "System", "inactive")
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Top row - Game state and metrics
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Game state display
        self.game_state_display = GameStateDisplay(self.top_frame)
        self.game_state_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Metrics display
        self.metrics_display = MetricsDisplay(self.top_frame)
        self.metrics_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Setup metrics
        self._setup_metrics()
        
        # Middle row - Players and activity
        self.middle_frame = ttk.Frame(self.main_frame)
        self.middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Players display
        self.players_display = PlayersDisplay(self.middle_frame)
        self.players_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Activity log
        self.activity_log = ActivityLog(self.middle_frame)
        self.activity_log.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Session statistics row
        self.session_frame = ttk.LabelFrame(self.main_frame, text="Session Statistics")
        self.session_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Session stats labels
        self.session_labels = {}
        stats_container = ttk.Frame(self.session_frame)
        stats_container.pack(fill=tk.X, padx=10, pady=5)
        
        # Create session stat labels
        stats = ["Uptime", "Hands", "Data Size", "Avg Accuracy", "Avg FPS", "Errors"]
        for i, stat in enumerate(stats):
            frame = ttk.Frame(stats_container)
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            label = tk.Label(frame, text=f"{stat}:", font=("Arial", 9))
            label.pack(anchor=tk.W)
            
            value_label = tk.Label(frame, text="--", font=("Arial", 9, "bold"), fg="blue")
            value_label.pack(anchor=tk.W)
            
            self.session_labels[stat.lower().replace(" ", "_")] = value_label
        
        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(self.control_frame, text="▶️ START", 
                                      command=self.on_start, state=tk.NORMAL)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(self.control_frame, text="⏸️ PAUSE", 
                                      command=self.on_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(self.control_frame, text="⏹️ STOP", 
                                     command=self.on_stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(self.control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.settings_button = ttk.Button(self.control_frame, text="⚙️ Settings", 
                                         command=self.on_settings)
        self.settings_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_button = ttk.Button(self.control_frame, text="📊 Export", 
                                       command=self.on_export)
        self.export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.debug_button = ttk.Button(self.control_frame, text="🔍 Safe Debug", 
                                      command=self.on_debug)
        self.debug_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.calibrate_button = ttk.Button(self.control_frame, text="🎯 Safe Calibrate", 
                                          command=self.on_calibrate)
        self.calibrate_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress charts frame
        self.charts_frame = ttk.LabelFrame(self.main_frame, text="Performance Charts")
        self.fps_chart = ProgressChart(self.charts_frame, "FPS", 200, 80)
        self.accuracy_chart = ProgressChart(self.charts_frame, "Accuracy %", 200, 80)
        
        # Initially hidden - can be shown via menu
        self.charts_visible = False
    
    def _setup_metrics(self) -> None:
        """Setup metrics display."""
        self.metrics_display.add_metric("cards_detected", "🎯 Cards", "{}/5")
        self.metrics_display.add_metric("text_accuracy", "📝 Text", "{:.1f}", "%")
        self.metrics_display.add_metric("frame_rate", "⚡ Speed", "{:.1f}", " FPS")
        self.metrics_display.add_metric("processing_time", "🧠 Processing", "{:.0f}", "ms")
        self.metrics_display.add_metric("errors", "❌ Errors", "{}")
    
    def _setup_layout(self) -> None:
        """Setup additional layout configurations."""
        # Configure weight for responsive resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.main_frame.columnconfigure(0, weight=1)
        self.middle_frame.columnconfigure(0, weight=1)
        self.middle_frame.columnconfigure(1, weight=1)
        self.middle_frame.rowconfigure(0, weight=1)
    
    def _start_update_thread(self) -> None:
        """Start background thread for UI updates."""
        self.stop_update_thread = False
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self) -> None:
        """Main update loop for dashboard."""
        while not self.stop_update_thread:
            try:
                if self.is_running:
                    self._update_displays()
                time.sleep(0.1)  # 100ms update interval
            except Exception as e:
                print(f"Update loop error: {e}")
                time.sleep(1)
    
    def _update_displays(self) -> None:
        """Update all displays with current data."""
        # Update game state
        if self.get_game_state_callback:
            game_state = self.get_game_state_callback()
            if game_state:
                self.root.after(0, self.game_state_display.update_game_state, game_state)
                
                # Update players
                players = game_state.get("players", [])
                self.root.after(0, self.players_display.update_players, players)
        
        # Update performance metrics
        if self.get_performance_stats_callback:
            stats = self.get_performance_stats_callback()
            self.root.after(0, self._update_metrics, stats)
        
        # Update session statistics
        if self.get_session_stats_callback:
            session_stats = self.get_session_stats_callback()
            self.root.after(0, self._update_session_stats, session_stats)
    
    def _update_metrics(self, stats: Dict[str, Any]) -> None:
        """Update metrics display."""
        # Cards detected
        community_cards = stats.get("community_cards_count", 0)
        self.metrics_display.update_metric("cards_detected", community_cards)
        
        # Text accuracy
        ocr_confidence = stats.get("text_ocr_confidence", 0) * 100
        self.metrics_display.update_metric("text_accuracy", ocr_confidence)
        
        # Frame rate
        fps = stats.get("frame_rate", 0)
        self.metrics_display.update_metric("frame_rate", fps)
        
        # Processing time
        processing_time = stats.get("processing_time_ms", 0)
        self.metrics_display.update_metric("processing_time", processing_time)
        
        # Errors
        errors = stats.get("errors_last_hour", 0)
        self.metrics_display.update_metric("errors", errors)
        
        # Update charts if visible
        if self.charts_visible:
            self.fps_chart.add_data_point(fps)
            self.accuracy_chart.add_data_point(ocr_confidence)
    
    def _update_session_stats(self, stats: Dict[str, Any]) -> None:
        """Update session statistics."""
        # Calculate uptime
        start_time = stats.get("start_time")
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                uptime = datetime.now() - start_dt.replace(tzinfo=None)
                hours = int(uptime.total_seconds() // 3600)
                minutes = int((uptime.total_seconds() % 3600) // 60)
                uptime_str = f"{hours}h {minutes}m"
            except:
                uptime_str = "--"
        else:
            uptime_str = "--"
        
        self.session_labels["uptime"].config(text=uptime_str)
        
        # Hands count
        hands = stats.get("total_hands", 0)
        self.session_labels["hands"].config(text=str(hands))
        
        # Data size (estimated)
        frames = stats.get("total_frames", 0)
        data_mb = int(frames * 0.01)  # Rough estimate
        self.session_labels["data_size"].config(text=f"{data_mb}MB")
        
        # Average accuracy
        avg_accuracy = stats.get("avg_card_confidence", 0) * 100
        self.session_labels["avg_accuracy"].config(text=f"{avg_accuracy:.1f}%")
        
        # Average FPS
        avg_fps = stats.get("avg_frame_rate", 0)
        self.session_labels["avg_fps"].config(text=f"{avg_fps:.1f}")
        
        # Errors
        errors = stats.get("recent_metrics_count", 0)
        self.session_labels["errors"].config(text=str(errors))
    
    def on_start(self) -> None:
        """Handle start button click."""
        if self.start_callback:
            self.start_callback()
            self.set_running_state(True)
            self.activity_logger.log_activity("System started")
    
    def on_pause(self) -> None:
        """Handle pause button click."""
        if self.is_running:
            self.set_running_state(False)
            self.activity_logger.log_activity("System paused")
    
    def on_stop(self) -> None:
        """Handle stop button click."""
        if self.stop_callback:
            self.stop_callback()
            self.set_running_state(False)
            self.activity_logger.log_activity("System stopped")
    
    def on_settings(self) -> None:
        """Handle settings button click."""
        if self.settings_callback:
            self.settings_callback()
        else:
            messagebox.showinfo("Settings", "Settings dialog not implemented yet.")
    
    def on_export(self) -> None:
        """Handle export button click."""
        try:
            if self.export_callback:
                filename = self.export_callback()
                if filename:
                    messagebox.showinfo("Export Complete", f"Data exported to:\n{filename}")
                    self.activity_logger.log_activity(f"Data exported to {filename}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export data")
            else:
                messagebox.showinfo("Export", "Export functionality not available")
        except Exception as e:
            messagebox.showerror("Export Error", f"Export failed: {str(e)}")
    
    def on_debug(self) -> None:
        """Handle debug button click."""
        if self.debug_callback:
            self.debug_callback()
        else:
            messagebox.showinfo("Debug", "Debug tools not available")
    
    def on_calibrate(self) -> None:
        """Handle calibrate button click."""
        if self.calibrate_callback:
            self.calibrate_callback()
        else:
            messagebox.showinfo("Calibrate", "Calibration tools not available")
    
    def set_running_state(self, running: bool) -> None:
        """Update UI state based on running status."""
        self.is_running = running
        
        if running:
            self.status_indicator.set_status("active")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_indicator.set_status("inactive")
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
    
    def set_session_id(self, session_id: int) -> None:
        """Set current session ID."""
        self.session_id = session_id
        self.root.title(f"Poker AI Vision Monitor v1.0 - Session {session_id}")
    
    def add_activity(self, message: str, level: str = "info") -> None:
        """Add activity to log."""
        self.activity_logger.log_activity(message, level)
        self.activity_log.add_activity(message, level)
    
    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        messagebox.showerror(title, message)
        self.add_activity(f"Error: {message}", "error")
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog."""
        messagebox.showwarning(title, message)
        self.add_activity(f"Warning: {message}", "warning")
    
    def show_info(self, title: str, message: str) -> None:
        """Show info dialog."""
        messagebox.showinfo(title, message)
        self.add_activity(f"Info: {message}")
    
    def toggle_charts(self) -> None:
        """Toggle performance charts visibility."""
        if self.charts_visible:
            self.charts_frame.pack_forget()
            self.charts_visible = False
        else:
            self.charts_frame.pack(fill=tk.X, pady=(10, 0))
            self.fps_chart.pack(side=tk.LEFT, padx=5, pady=5)
            self.accuracy_chart.pack(side=tk.LEFT, padx=5, pady=5)
            self.charts_visible = True
    
    def on_closing(self) -> None:
        """Handle window closing."""
        if self.is_running:
            result = messagebox.askyesno("Confirm Exit", 
                                        "System is still running. Stop and exit?")
            if result:
                self.on_stop()
            else:
                return
        
        self.stop_update_thread = True
        if self.update_thread:
            self.update_thread.join(timeout=1)
        
        self.root.destroy()
    
    def run(self) -> None:
        """Start the main GUI loop."""
        self.root.mainloop()
    
    # Callback setters
    def set_start_callback(self, callback: Callable[[], None]) -> None:
        self.start_callback = callback
    
    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        self.stop_callback = callback
    
    def set_export_callback(self, callback: Callable[[], str]) -> None:
        self.export_callback = callback
    
    def set_settings_callback(self, callback: Callable[[], None]) -> None:
        self.settings_callback = callback
    
    def set_get_game_state_callback(self, callback: Callable[[], Optional[Dict[str, Any]]]) -> None:
        self.get_game_state_callback = callback
    
    def set_get_performance_stats_callback(self, callback: Callable[[], Dict[str, Any]]) -> None:
        self.get_performance_stats_callback = callback
    
    def set_get_session_stats_callback(self, callback: Callable[[], Dict[str, Any]]) -> None:
        self.get_session_stats_callback = callback
    
    def set_debug_callback(self, callback: Callable[[], None]) -> None:
        self.debug_callback = callback
    
    def set_calibrate_callback(self, callback: Callable[[], None]) -> None:
        self.calibrate_callback = callback