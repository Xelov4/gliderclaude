"""Debug and visualization tools for vision system."""
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..data.models import Card, Player, GameState
from .detection import CardDetector
from .ocr import TextRecognizer


class VisionDebugger:
    """Interactive vision debugging and annotation tool."""
    
    def __init__(self):
        self.card_detector = CardDetector()
        self.text_recognizer = TextRecognizer()
        self.current_image = None
        self.detections = {}
        self.annotations = {}
        
    def launch_debugger(self):
        """Launch the debug GUI."""
        self.root = tk.Tk()
        self.root.title("Poker Vision Debugger")
        self.root.geometry("1200x800")
        
        self._create_debug_gui()
        self.root.mainloop()
    
    def _create_debug_gui(self):
        """Create debug GUI interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # File operations
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Load Image", command=self._load_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Save Screenshot", command=self._save_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Live Capture", command=self._start_live_capture).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(file_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Detection operations
        ttk.Button(file_frame, text="Detect Cards", command=self._detect_cards).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Run OCR", command=self._run_ocr).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Parse Game State", command=self._parse_game_state).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(file_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Annotation tools
        ttk.Button(file_frame, text="Annotate", command=self._start_annotation).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Clear", command=self._clear_detections).pack(side=tk.LEFT, padx=2)
        
        # Settings frame
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Confidence thresholds
        ttk.Label(settings_frame, text="Card Confidence:").pack(side=tk.LEFT, padx=2)
        self.card_confidence = tk.DoubleVar(value=0.8)
        ttk.Scale(settings_frame, from_=0.1, to=1.0, variable=self.card_confidence, 
                 orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(settings_frame, text="OCR Confidence:").pack(side=tk.LEFT, padx=10)
        self.ocr_confidence = tk.DoubleVar(value=0.7)
        ttk.Scale(settings_frame, from_=0.1, to=1.0, variable=self.ocr_confidence, 
                 orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT, padx=2)
        
        # Show/hide options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.show_cards = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show Cards", variable=self.show_cards, 
                       command=self._update_display).pack(side=tk.LEFT, padx=5)
        
        self.show_text = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show Text", variable=self.show_text,
                       command=self._update_display).pack(side=tk.LEFT, padx=5)
        
        self.show_regions = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show Regions", variable=self.show_regions,
                       command=self._update_display).pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image display
        image_frame = ttk.LabelFrame(content_frame, text="Image")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(image_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Info panel
        info_frame = ttk.LabelFrame(content_frame, text="Detection Results")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Results text
        self.results_text = tk.Text(info_frame, width=40, height=20, font=("Courier", 9))
        results_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _load_image(self):
        """Load image from file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if file_path:
            self.current_image = cv2.imread(file_path)
            if self.current_image is not None:
                self._display_image()
                self.status_label.config(text=f"Loaded: {Path(file_path).name}")
            else:
                messagebox.showerror("Error", "Failed to load image")
    
    def _save_screenshot(self):
        """Save current screenshot."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_screenshot_{timestamp}.png"
        
        save_path = filedialog.asksaveasfilename(
            title="Save Screenshot",
            defaultextension=".png",
            initialvalue=filename,
            filetypes=[("PNG files", "*.png")]
        )
        
        if save_path:
            # Save image with annotations
            annotated_image = self._create_annotated_image()
            cv2.imwrite(save_path, annotated_image)
            self.status_label.config(text=f"Saved: {Path(save_path).name}")
    
    def _start_live_capture(self):
        """Start SAFE live capture from screen."""
        try:
            # Use safe screen capture method
            import mss
            
            screen_capture = mss.mss()
            
            # Get primary monitor
            monitor = screen_capture.monitors[1] if len(screen_capture.monitors) > 1 else screen_capture.monitors[0]
            
            # Capture screenshot
            screenshot = screen_capture.grab(monitor)
            
            # Convert to numpy array
            import numpy as np
            frame = np.array(screenshot)
            
            # Convert BGRA to BGR if needed
            if frame.shape[2] == 4:
                import cv2
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            if frame is not None:
                self.current_image = frame
                self._display_image()
                self.status_label.config(text="SAFE live capture - single frame")
            else:
                messagebox.showerror("Error", "Failed to capture screen")
                
        except Exception as e:
            messagebox.showerror("Error", f"SAFE capture failed: {str(e)}")
    
    def _detect_cards(self):
        """Run card detection on current image."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        self.status_label.config(text="Detecting cards...")
        
        # Update detector confidence
        self.card_detector.confidence_threshold = self.card_confidence.get()
        
        # Detect cards in full image
        cards = self.card_detector.detect_cards(self.current_image)
        
        self.detections['cards'] = cards
        
        # Update results
        self._update_results()
        self._update_display()
        
        self.status_label.config(text=f"Detected {len(cards)} cards")
    
    def _run_ocr(self):
        """Run OCR on current image."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        self.status_label.config(text="Running OCR...")
        
        # Extract text from full image
        text_elements = self.text_recognizer.extract_text(self.current_image)
        
        self.detections['text'] = text_elements
        
        # Update results
        self._update_results()
        self._update_display()
        
        self.status_label.config(text=f"Found {len(text_elements)} text elements")
    
    def _parse_game_state(self):
        """Parse complete game state."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        self.status_label.config(text="Parsing game state...")
        
        # Import here to avoid circular imports
        from .state_parser import GameStateParser
        
        parser = GameStateParser()
        game_state = parser.parse_game_state(self.current_image, datetime.now())
        
        if game_state:
            self.detections['game_state'] = game_state
            self._update_results()
            self.status_label.config(text="Game state parsed successfully")
        else:
            self.status_label.config(text="Failed to parse game state")
            messagebox.showerror("Error", "Failed to parse game state")
    
    def _start_annotation(self):
        """Start manual annotation mode."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        annotation_dialog = AnnotationDialog(self.root, self.current_image)
        annotations = annotation_dialog.get_annotations()
        
        if annotations:
            self.annotations = annotations
            self._update_display()
    
    def _clear_detections(self):
        """Clear all detections and annotations."""
        self.detections.clear()
        self.annotations.clear()
        self._update_results()
        self._update_display()
        self.status_label.config(text="Cleared detections")
    
    def _display_image(self):
        """Display current image on canvas."""
        if self.current_image is None:
            return
        
        # Create annotated image
        display_image = self._create_annotated_image()
        
        # Convert to PhotoImage
        img_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _create_annotated_image(self) -> np.ndarray:
        """Create image with all annotations."""
        if self.current_image is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)
        
        annotated = self.current_image.copy()
        
        # Draw cards
        if self.show_cards.get() and 'cards' in self.detections:
            for card in self.detections['cards']:
                x, y = card.position
                # Draw circle for card center
                cv2.circle(annotated, (x, y), 15, (0, 255, 0), 2)
                # Draw card text
                text = f"{card.rank}{card.suit} ({card.confidence:.2f})"
                cv2.putText(annotated, text, (x-20, y-20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 255, 0), 2)
        
        # Draw text detections
        if self.show_text.get() and 'text' in self.detections:
            for text_elem in self.detections['text']:
                bbox = text_elem['bbox']
                if len(bbox) >= 4:
                    # Draw bounding box
                    points = np.array(bbox, dtype=np.int32)
                    cv2.polylines(annotated, [points], True, (255, 0, 0), 2)
                    # Draw text
                    text = f"{text_elem['text']} ({text_elem['confidence']:.2f})"
                    cv2.putText(annotated, text, (int(bbox[0][0]), int(bbox[0][1])-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw regions from settings
        if self.show_regions.get():
            from ..config.settings import settings
            regions = settings.game_client.table_regions
            
            colors = {
                'community_cards': (0, 255, 255),  # Yellow
                'pot_display': (255, 0, 255),       # Magenta
                'timer': (255, 255, 0),             # Cyan
                'player_0': (128, 255, 128),        # Light green
                'player_1': (255, 128, 128),        # Light red
                'player_2': (128, 128, 255)         # Light blue
            }
            
            for region_name, region in regions.items():
                color = colors.get(region_name, (255, 255, 255))
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
                cv2.putText(annotated, region_name, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, color, 1)
        
        return annotated
    
    def _update_results(self):
        """Update results text display."""
        self.results_text.delete(1.0, tk.END)
        
        if 'cards' in self.detections:
            self.results_text.insert(tk.END, f"=== CARDS ({len(self.detections['cards'])}) ===\n")
            for i, card in enumerate(self.detections['cards']):
                self.results_text.insert(tk.END, 
                    f"{i+1}. {card.rank}{card.suit} @ {card.position} (conf: {card.confidence:.3f})\n")
            self.results_text.insert(tk.END, "\n")
        
        if 'text' in self.detections:
            self.results_text.insert(tk.END, f"=== TEXT ({len(self.detections['text'])}) ===\n")
            for i, text_elem in enumerate(self.detections['text']):
                self.results_text.insert(tk.END, 
                    f"{i+1}. '{text_elem['text']}' (conf: {text_elem['confidence']:.3f})\n")
            self.results_text.insert(tk.END, "\n")
        
        if 'game_state' in self.detections:
            game_state = self.detections['game_state']
            self.results_text.insert(tk.END, "=== GAME STATE ===\n")
            self.results_text.insert(tk.END, f"Hand ID: {game_state.hand_id}\n")
            self.results_text.insert(tk.END, f"Phase: {game_state.game_phase.value}\n")
            self.results_text.insert(tk.END, f"Pot: {game_state.pot_size}\n")
            self.results_text.insert(tk.END, f"Timer: {game_state.timer_remaining}s\n")
            self.results_text.insert(tk.END, f"Community Cards: {len(game_state.community_cards)}\n")
            self.results_text.insert(tk.END, f"Players: {len(game_state.players)}\n")
            
            for player in game_state.players:
                status = "CURRENT" if player.is_current else "ACTIVE" if player.is_active else "FOLDED"
                self.results_text.insert(tk.END, 
                    f"  {player.name}: {player.stack_size} chips, {len(player.hole_cards)} cards [{status}]\n")
    
    def _update_display(self):
        """Update image display with current settings."""
        self._display_image()


class AnnotationDialog:
    """Dialog for manual annotation of images."""
    
    def __init__(self, parent, image):
        self.parent = parent
        self.image = image
        self.annotations = {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manual Annotation")
        self.dialog.geometry("800x600")
        self.dialog.grab_set()
        
        self._create_annotation_gui()
    
    def _create_annotation_gui(self):
        """Create annotation interface."""
        # Instructions
        instructions = tk.Label(self.dialog, 
            text="Click on cards and enter their values. Use format: 'As' for Ace of Spades, 'Kh' for King of Hearts, etc.",
            wraplength=780, justify=tk.LEFT)
        instructions.pack(pady=10)
        
        # Canvas for image
        self.canvas = tk.Canvas(self.dialog, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display image
        img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        
        # Scale image to fit
        canvas_width = 780
        canvas_height = 400
        img_width, img_height = pil_image.size
        
        scale = min(canvas_width/img_width, canvas_height/img_height, 1.0)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        pil_image = pil_image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(400, 200, image=self.photo)
        
        # Bind click events
        self.canvas.bind("<Button-1>", self._on_click)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Done", command=self._on_done).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        
        self.result = None
    
    def _on_click(self, event):
        """Handle click on image."""
        # Get card value from user
        card_dialog = tk.Toplevel(self.dialog)
        card_dialog.title("Card Value")
        card_dialog.geometry("300x150")
        card_dialog.grab_set()
        
        tk.Label(card_dialog, text="Enter card value (e.g., 'As', 'Kh', '10c'):").pack(pady=10)
        
        entry = tk.Entry(card_dialog, font=("Arial", 12))
        entry.pack(pady=5)
        entry.focus()
        
        def on_ok():
            value = entry.get().strip()
            if value:
                # Store annotation
                self.annotations[len(self.annotations)] = {
                    'position': (event.x, event.y),
                    'value': value,
                    'type': 'card'
                }
                
                # Draw annotation on canvas
                self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, 
                                       fill="red", outline="red")
                self.canvas.create_text(event.x, event.y-15, text=value, fill="red")
            
            card_dialog.destroy()
        
        ttk.Button(card_dialog, text="OK", command=on_ok).pack(pady=10)
        entry.bind('<Return>', lambda e: on_ok())
    
    def _on_done(self):
        """Finish annotation."""
        self.result = self.annotations
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Cancel annotation."""
        self.result = None
        self.dialog.destroy()
    
    def get_annotations(self):
        """Get annotation results."""
        self.dialog.wait_window()
        return self.result