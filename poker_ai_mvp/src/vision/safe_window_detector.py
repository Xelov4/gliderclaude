"""Safe window detection without intrusive methods."""
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple, Optional
from loguru import logger
import mss

from ..config.settings import settings


class SafeWindowDetector:
    """Detect windows using only safe, non-intrusive methods."""
    
    def __init__(self):
        self.screen_capture = mss.mss()
        self.target_region = None
        
    def select_screen_region_interactive(self) -> Optional[Dict]:
        """Interactive screen region selection using safe methods."""
        # Take full screen capture first
        full_screen = self._capture_full_screen()
        if full_screen is None:
            messagebox.showerror("Error", "Failed to capture screen")
            return None
        
        # Show region selection dialog
        region_selector = RegionSelector(full_screen)
        selected_region = region_selector.select_region()
        
        if selected_region:
            self.target_region = selected_region
            logger.info(f"Selected screen region: {selected_region}")
            
        return selected_region
    
    def _capture_full_screen(self) -> Optional[np.ndarray]:
        """Capture full screen using safe MSS method."""
        try:
            # Get all monitors
            monitors = self.screen_capture.monitors
            
            # Use primary monitor (index 1, index 0 is all monitors combined)
            monitor = monitors[1] if len(monitors) > 1 else monitors[0]
            
            # Capture screenshot
            screenshot = self.screen_capture.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert BGRA to BGR
            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None
    
    def get_target_screenshot(self) -> Optional[np.ndarray]:
        """Get screenshot of target region using safe methods."""
        if not self.target_region:
            logger.warning("No target region selected")
            return None
        
        try:
            # Capture the specific region
            region = {
                "top": self.target_region["y"],
                "left": self.target_region["x"],
                "width": self.target_region["width"],
                "height": self.target_region["height"]
            }
            
            screenshot = self.screen_capture.grab(region)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert BGRA to BGR
            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture target region: {e}")
            return None


class RegionSelector:
    """Interactive region selection tool using safe methods."""
    
    def __init__(self, full_screen_image: np.ndarray):
        self.full_screen = full_screen_image
        self.selected_region = None
        
    def select_region(self) -> Optional[Dict]:
        """Show interactive region selection dialog."""
        # Create selection window
        root = tk.Tk()
        root.title("Select Poker Client Region")
        root.state('zoomed')  # Maximize window
        
        # Instructions
        instructions = tk.Label(root, 
            text="INSTRUCTIONS:\n"
                 "1. You will see your full screen below\n"
                 "2. Click and drag to select the poker client area\n"
                 "3. Click 'Confirm Selection' when done\n"
                 "4. This is completely safe - no window manipulation",
            font=("Arial", 12), bg="yellow", fg="black", justify=tk.LEFT)
        instructions.pack(fill=tk.X, pady=10)
        
        # Control frame
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, pady=5)
        
        status_label = tk.Label(control_frame, text="Click and drag to select poker client area", 
                               font=("Arial", 10))
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        confirm_btn = tk.Button(control_frame, text="Confirm Selection", 
                               command=lambda: self._confirm_selection(root),
                               bg="green", fg="white", font=("Arial", 10, "bold"))
        confirm_btn.pack(side=tk.RIGHT, padx=10)
        
        cancel_btn = tk.Button(control_frame, text="Cancel", 
                              command=lambda: self._cancel_selection(root),
                              bg="red", fg="white", font=("Arial", 10))
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Canvas for image display
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="black")
        
        # Scrollbars
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Display screen image
        self._display_screen_image(canvas)
        
        # Selection state
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.canvas = canvas
        self.status_label = status_label
        
        # Bind mouse events
        canvas.bind("<Button-1>", self._on_mouse_down)
        canvas.bind("<B1-Motion>", self._on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        
        # Wait for user action
        root.mainloop()
        
        return self.selected_region
    
    def _display_screen_image(self, canvas):
        """Display full screen image on canvas."""
        # Convert to PIL format for Tkinter
        from PIL import Image, ImageTk
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(self.full_screen, cv2.COLOR_BGR2RGB)
        
        # Create PIL image
        pil_image = Image.fromarray(rgb_image)
        
        # Store reference to prevent garbage collection
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # Display on canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def _on_mouse_down(self, event):
        """Start region selection."""
        # Convert canvas coordinates to image coordinates
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        self.status_label.config(text=f"Selection started at ({int(self.start_x)}, {int(self.start_y)})")
    
    def _on_mouse_drag(self, event):
        """Update selection rectangle."""
        if self.start_x is not None and self.start_y is not None:
            # Convert canvas coordinates
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            # Remove previous rectangle
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # Draw new rectangle
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline="red", width=3
            )
            
            # Update status
            width = abs(current_x - self.start_x)
            height = abs(current_y - self.start_y)
            self.status_label.config(text=f"Selection: {int(width)}x{int(height)}")
    
    def _on_mouse_up(self, event):
        """Finish region selection."""
        if self.start_x is not None and self.start_y is not None:
            # Convert canvas coordinates
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            # Calculate region bounds
            x1 = int(min(self.start_x, end_x))
            y1 = int(min(self.start_y, end_y))
            x2 = int(max(self.start_x, end_x))
            y2 = int(max(self.start_y, end_y))
            
            # Store selection
            self.selected_region = {
                "x": x1,
                "y": y1,
                "width": x2 - x1,
                "height": y2 - y1
            }
            
            self.status_label.config(text=f"Selected: {x1},{y1} {x2-x1}x{y2-y1} - Click 'Confirm Selection'")
    
    def _confirm_selection(self, root):
        """Confirm the selection."""
        if self.selected_region:
            root.quit()
            root.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a region first")
    
    def _cancel_selection(self, root):
        """Cancel the selection."""
        self.selected_region = None
        root.quit()
        root.destroy()


class SafeRegionCalibrator:
    """Safe region calibration using screen capture only."""
    
    def __init__(self, window_detector: SafeWindowDetector):
        self.window_detector = window_detector
        self.regions = {}
        
    def calibrate_regions(self) -> Dict:
        """Calibrate detection regions safely."""
        if not self.window_detector.target_region:
            messagebox.showerror("Error", "No target region selected!")
            return {}
        
        # Get screenshot of target region
        screenshot = self.window_detector.get_target_screenshot()
        if screenshot is None:
            messagebox.showerror("Error", "Failed to capture target region!")
            return {}
        
        # Launch region definition dialog
        dialog = RegionDefinitionDialog(screenshot)
        regions = dialog.define_regions()
        
        if regions:
            self.regions = regions
            logger.info(f"Calibrated {len(regions)} regions")
        
        return regions


class RegionDefinitionDialog:
    """Dialog for defining poker game regions safely."""
    
    def __init__(self, poker_image: np.ndarray):
        self.poker_image = poker_image
        self.regions = {}
        
    def define_regions(self) -> Dict:
        """Define poker game regions interactively."""
        root = tk.Tk()
        root.title("Define Poker Game Regions - SAFE MODE")
        root.geometry("1000x700")
        
        # Instructions
        instructions = tk.Text(root, height=4, wrap=tk.WORD)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        instructions.insert(tk.END, 
            "SAFE REGION CALIBRATION:\n"
            "This tool only uses screenshots - no window manipulation or injection.\n"
            "Click the buttons below to define regions, then click and drag on the image.\n"
            "Define: Community Cards, Pot Display, Timer, and Player positions.")
        instructions.config(state=tk.DISABLED)
        
        # Control buttons
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        regions_to_define = [
            ("Community Cards", "community_cards"),
            ("Pot Display", "pot_display"), 
            ("Timer", "timer"),
            ("Player 0 (You)", "player_0"),
            ("Player 1", "player_1"),
            ("Player 2", "player_2")
        ]
        
        for label, key in regions_to_define:
            btn = tk.Button(control_frame, text=f"Define {label}",
                           command=lambda k=key, l=label: self._start_region_definition(k, l))
            btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="Done", command=lambda: self._finish(root),
                 bg="green", fg="white").pack(side=tk.RIGHT, padx=10)
        
        # Canvas for poker image
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Display poker image
        self._display_poker_image()
        
        # Status
        self.status_label = tk.Label(root, text="Ready - Click a 'Define' button to start", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Selection state
        self.current_region_key = None
        self.current_region_label = None
        self.selecting = False
        
        root.mainloop()
        return self.regions
    
    def _display_poker_image(self):
        """Display poker screenshot on canvas."""
        from PIL import Image, ImageTk
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(self.poker_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _start_region_definition(self, region_key: str, region_label: str):
        """Start defining a specific region."""
        self.current_region_key = region_key
        self.current_region_label = region_label
        self.selecting = True
        
        self.status_label.config(text=f"Click and drag to define {region_label}")
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_region_start)
        self.canvas.bind("<B1-Motion>", self._on_region_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_region_end)
    
    def _on_region_start(self, event):
        """Start region selection."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect_id = None
    
    def _on_region_drag(self, event):
        """Update region selection."""
        if hasattr(self, 'start_x'):
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline="red", width=2
            )
    
    def _on_region_end(self, event):
        """Finish region selection."""
        if hasattr(self, 'start_x'):
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            # Calculate region
            x1 = int(min(self.start_x, end_x))
            y1 = int(min(self.start_y, end_y))
            x2 = int(max(self.start_x, end_x))
            y2 = int(max(self.start_y, end_y))
            
            # Store region
            self.regions[self.current_region_key] = {
                "x": x1,
                "y": y1,
                "w": x2 - x1,
                "h": y2 - y1
            }
            
            self.status_label.config(text=f"{self.current_region_label} defined: {x1},{y1} {x2-x1}x{y2-y1}")
            
            # Unbind mouse events
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            
            self.selecting = False
    
    def _finish(self, root):
        """Finish region definition."""
        root.quit()
        root.destroy()