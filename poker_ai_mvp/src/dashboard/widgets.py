"""Custom tkinter widgets for the dashboard."""
import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable


class StatusIndicator(tk.Frame):
    """Status indicator with colored circle."""
    
    def __init__(self, parent, label: str = "", initial_status: str = "inactive"):
        super().__init__(parent)
        
        self.label_text = label
        self.status = initial_status
        
        # Create widgets
        self.canvas = tk.Canvas(self, width=20, height=20, bg=self["bg"])
        self.canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        self.label = tk.Label(self, text=label, font=("Arial", 9))
        self.label.pack(side=tk.LEFT)
        
        self.update_display()
    
    def set_status(self, status: str) -> None:
        """Update status and visual indicator."""
        self.status = status
        self.update_display()
    
    def update_display(self) -> None:
        """Update visual display based on status."""
        self.canvas.delete("all")
        
        colors = {
            "active": "#00FF00",    # Green
            "warning": "#FFA500",   # Orange
            "error": "#FF0000",     # Red
            "inactive": "#808080"   # Gray
        }
        
        color = colors.get(self.status, "#808080")
        self.canvas.create_oval(2, 2, 18, 18, fill=color, outline="")
        
        # Update label if needed
        status_text = f"{self.label_text}: {self.status.upper()}"
        self.label.config(text=status_text)


class MetricsDisplay(tk.Frame):
    """Display for key metrics with labels and values."""
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.RIDGE, bd=1)
        
        self.metrics = {}
        self.metric_labels = {}
        
        # Title
        self.title = tk.Label(self, text="Performance Metrics", font=("Arial", 10, "bold"))
        self.title.pack(pady=(5, 10))
        
        # Metrics container
        self.metrics_frame = tk.Frame(self)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def add_metric(self, key: str, label: str, format_str: str = "{:.1f}", unit: str = "") -> None:
        """Add a new metric to display."""
        frame = tk.Frame(self.metrics_frame)
        frame.pack(fill=tk.X, pady=2)
        
        label_widget = tk.Label(frame, text=f"{label}:", font=("Arial", 9))
        label_widget.pack(side=tk.LEFT)
        
        value_widget = tk.Label(frame, text="--", font=("Arial", 9, "bold"), fg="blue")
        value_widget.pack(side=tk.RIGHT)
        
        self.metric_labels[key] = {
            "value": value_widget,
            "format": format_str,
            "unit": unit
        }
        
        self.metrics[key] = 0
    
    def update_metric(self, key: str, value: Any) -> None:
        """Update metric value."""
        if key in self.metrics:
            self.metrics[key] = value
            
            if key in self.metric_labels:
                format_str = self.metric_labels[key]["format"]
                unit = self.metric_labels[key]["unit"]
                
                try:
                    if isinstance(value, (int, float)):
                        formatted_value = format_str.format(value)
                    else:
                        formatted_value = str(value)
                    
                    display_text = f"{formatted_value}{unit}"
                    self.metric_labels[key]["value"].config(text=display_text)
                except Exception:
                    self.metric_labels[key]["value"].config(text=str(value))


class GameStateDisplay(tk.Frame):
    """Display current game state information."""
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.RIDGE, bd=1)
        
        # Title
        self.title = tk.Label(self, text="Live Game State", font=("Arial", 10, "bold"))
        self.title.pack(pady=(5, 10))
        
        # Game info frame
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Hand info
        self.hand_frame = tk.Frame(self.info_frame)
        self.hand_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(self.hand_frame, text="Hand:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.hand_label = tk.Label(self.hand_frame, text="--", font=("Arial", 9, "bold"))
        self.hand_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Phase info
        self.phase_frame = tk.Frame(self.info_frame)
        self.phase_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(self.phase_frame, text="Phase:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.phase_label = tk.Label(self.phase_frame, text="--", font=("Arial", 9, "bold"))
        self.phase_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Pot info
        self.pot_frame = tk.Frame(self.info_frame)
        self.pot_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(self.pot_frame, text="Pot:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.pot_label = tk.Label(self.pot_frame, text="--", font=("Arial", 9, "bold"))
        self.pot_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Timer info
        self.timer_frame = tk.Frame(self.info_frame)
        self.timer_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(self.timer_frame, text="Timer:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.timer_label = tk.Label(self.timer_frame, text="--", font=("Arial", 9, "bold"))
        self.timer_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Community cards
        self.cards_frame = tk.Frame(self.info_frame)
        self.cards_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(self.cards_frame, text="Community:", font=("Arial", 9)).pack(anchor=tk.W)
        self.cards_label = tk.Label(self.cards_frame, text="--", font=("Arial", 9, "bold"), fg="darkgreen")
        self.cards_label.pack(anchor=tk.W, padx=(10, 0))
    
    def update_game_state(self, game_state: Dict[str, Any]) -> None:
        """Update display with new game state."""
        try:
            # Update hand ID
            hand_id = game_state.get("hand_id", "Unknown")
            self.hand_label.config(text=hand_id[-8:] if len(hand_id) > 8 else hand_id)
            
            # Update phase
            phase = game_state.get("game_phase", "unknown").title()
            self.phase_label.config(text=phase)
            
            # Update pot
            pot_size = game_state.get("pot_size", 0)
            self.pot_label.config(text=f"{pot_size} chips")
            
            # Update timer
            timer = game_state.get("timer_remaining", 0)
            minutes = timer // 60
            seconds = timer % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Update community cards
            community_cards = game_state.get("community_cards", [])
            if community_cards:
                cards_text = " ".join([f"{card['rank']}{card['suit']}" for card in community_cards])
                self.cards_label.config(text=cards_text)
            else:
                self.cards_label.config(text="No cards dealt")
                
        except Exception as e:
            print(f"Error updating game state display: {e}")


class PlayersDisplay(tk.Frame):
    """Display player information."""
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.RIDGE, bd=1)
        
        # Title
        self.title = tk.Label(self, text="Players", font=("Arial", 10, "bold"))
        self.title.pack(pady=(5, 10))
        
        # Players container
        self.players_frame = tk.Frame(self)
        self.players_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.player_widgets = {}
    
    def update_players(self, players: List[Dict[str, Any]]) -> None:
        """Update player display."""
        # Clear existing widgets
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        self.player_widgets.clear()
        
        for player in players:
            self._create_player_widget(player)
    
    def _create_player_widget(self, player: Dict[str, Any]) -> None:
        """Create widget for single player."""
        position = player.get("position", 0)
        name = player.get("name", "Unknown")
        stack_size = player.get("stack_size", 0)
        hole_cards = player.get("hole_cards", [])
        current_bet = player.get("current_bet", 0)
        is_current = player.get("is_current", False)
        is_active = player.get("is_active", True)
        
        # Player frame
        player_frame = tk.Frame(self.players_frame, relief=tk.GROOVE, bd=1)
        player_frame.pack(fill=tk.X, pady=2)
        
        # Background color for current player
        if is_current:
            player_frame.config(bg="#FFFACD")  # Light yellow
        elif not is_active:
            player_frame.config(bg="#F5F5F5")  # Light gray
        
        # Player info
        info_frame = tk.Frame(player_frame, bg=player_frame["bg"])
        info_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Name and position
        name_text = f"👤 {name} (Pos {position})"
        if is_current:
            name_text += " [CURRENT]"
        
        name_label = tk.Label(info_frame, text=name_text, font=("Arial", 9, "bold"), bg=info_frame["bg"])
        name_label.pack(anchor=tk.W)
        
        # Stack and bet info
        stack_text = f"Stack: {stack_size}"
        if current_bet > 0:
            stack_text += f" | Bet: {current_bet}"
        
        stack_label = tk.Label(info_frame, text=stack_text, font=("Arial", 8), bg=info_frame["bg"])
        stack_label.pack(anchor=tk.W, padx=(10, 0))
        
        # Hole cards
        if hole_cards:
            cards_text = " ".join([f"{card['rank']}{card['suit']}" for card in hole_cards])
        else:
            cards_text = "?? ??"
        
        cards_label = tk.Label(info_frame, text=f"Cards: {cards_text}", 
                              font=("Arial", 8), fg="darkblue", bg=info_frame["bg"])
        cards_label.pack(anchor=tk.W, padx=(10, 0))
        
        self.player_widgets[position] = player_frame


class ActivityLog(tk.Frame):
    """Scrollable activity log."""
    
    def __init__(self, parent, max_entries: int = 100):
        super().__init__(parent, relief=tk.RIDGE, bd=1)
        
        self.max_entries = max_entries
        
        # Title
        self.title = tk.Label(self, text="Recent Activity", font=("Arial", 10, "bold"))
        self.title.pack(pady=(5, 5))
        
        # Create text widget with scrollbar
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.text_widget = tk.Text(self.text_frame, height=8, width=40, 
                                  font=("Courier", 8), wrap=tk.WORD, state=tk.DISABLED)
        
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for different log levels
        self.text_widget.tag_configure("info", foreground="black")
        self.text_widget.tag_configure("warning", foreground="orange")
        self.text_widget.tag_configure("error", foreground="red")
        
        self.entry_count = 0
    
    def add_activity(self, message: str, level: str = "info") -> None:
        """Add activity message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, formatted_message, level)
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        
        # Limit number of entries
        self.entry_count += 1
        if self.entry_count > self.max_entries:
            # Remove oldest entries
            lines = self.text_widget.get("1.0", tk.END).split("\n")
            if len(lines) > self.max_entries:
                excess_lines = len(lines) - self.max_entries
                self.text_widget.delete("1.0", f"{excess_lines + 1}.0")
                self.entry_count = self.max_entries
        
        self.text_widget.config(state=tk.DISABLED)
    
    def clear_log(self) -> None:
        """Clear all log entries."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.entry_count = 0


class ProgressChart(tk.Frame):
    """Simple progress chart using Canvas."""
    
    def __init__(self, parent, title: str = "Progress", width: int = 300, height: int = 100):
        super().__init__(parent, relief=tk.RIDGE, bd=1)
        
        self.title_text = title
        self.width = width
        self.height = height
        self.data_points = []
        self.max_points = 50
        
        # Title
        self.title = tk.Label(self, text=title, font=("Arial", 9, "bold"))
        self.title.pack(pady=(5, 2))
        
        # Canvas for chart
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white")
        self.canvas.pack(padx=5, pady=(0, 5))
        
        self.draw_axes()
    
    def add_data_point(self, value: float) -> None:
        """Add new data point and redraw chart."""
        self.data_points.append(value)
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points = self.data_points[-self.max_points:]
        
        self.draw_chart()
    
    def draw_axes(self) -> None:
        """Draw chart axes."""
        self.canvas.delete("axes")
        
        # Draw axes
        self.canvas.create_line(30, self.height - 20, self.width - 10, self.height - 20, 
                               fill="black", width=1, tags="axes")  # X-axis
        self.canvas.create_line(30, 10, 30, self.height - 20, 
                               fill="black", width=1, tags="axes")  # Y-axis
    
    def draw_chart(self) -> None:
        """Draw chart with current data."""
        self.canvas.delete("data")
        self.draw_axes()
        
        if len(self.data_points) < 2:
            return
        
        # Calculate scaling
        max_value = max(self.data_points) if self.data_points else 1
        min_value = min(self.data_points) if self.data_points else 0
        value_range = max_value - min_value if max_value != min_value else 1
        
        x_step = (self.width - 40) / (len(self.data_points) - 1)
        y_scale = (self.height - 30) / value_range
        
        # Draw line
        points = []
        for i, value in enumerate(self.data_points):
            x = 30 + i * x_step
            y = self.height - 20 - (value - min_value) * y_scale
            points.extend([x, y])
        
        if len(points) >= 4:  # Need at least 2 points
            self.canvas.create_line(points, fill="blue", width=2, tags="data")
        
        # Draw value labels
        if self.data_points:
            current_value = self.data_points[-1]
            self.canvas.create_text(self.width - 10, 10, text=f"{current_value:.1f}", 
                                   anchor=tk.NE, font=("Arial", 8), tags="data")