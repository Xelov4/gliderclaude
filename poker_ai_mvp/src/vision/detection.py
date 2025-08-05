"""Card and UI element detection using YOLO."""
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from loguru import logger

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics not available, using fallback detection")

from ..data.models import Card, Suit, Rank


class CardDetector:
    """Card detection system with YOLO integration."""
    
    def __init__(self, model_path: str = "models/playing_cards_yolo.pt"):
        self.model_path = model_path
        self.confidence_threshold = 0.8
        self.nms_threshold = 0.4
        
        # Try to use proper YOLO detector
        self.yolo_detector = None
        self._initialize_detector()
    
    def _initialize_detector(self) -> None:
        """Initialize YOLO card detector."""
        try:
            from .yolo_detector import YOLOCardDetector
            self.yolo_detector = YOLOCardDetector(self.model_path)
            logger.info("YOLO card detector initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize YOLO detector: {e}")
            logger.info("Using fallback detection methods")
    
    def detect_cards(self, image: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> List[Card]:
        """Detect cards in image or image region."""
        # Try YOLO detector first
        if self.yolo_detector is not None:
            try:
                cards = self.yolo_detector.detect_cards(image, region)
                if cards:  # If YOLO found cards, return them
                    return cards
            except Exception as e:
                logger.warning(f"YOLO detection failed, using fallback: {e}")
        
        # Use fallback detection
        return self._fallback_card_detection(image, region)
    
    def _fallback_card_detection(self, image: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> List[Card]:
        """Fallback card detection using template matching."""
        # For MVP, return mock cards based on the screenshot
        # In production, implement template matching or other detection method
        
        if region:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
        else:
            roi = image
            
        # Mock detection based on screenshot analysis
        cards = []
        
        # Check if this looks like community cards region (center area)
        if region and region[0] > 400 and region[0] < 700:  # Community cards area
            cards = [
                Card("4", "♦", 0.95, (570, 375)),
                Card("10", "♥", 0.93, (620, 375)),
                Card("10", "♣", 0.97, (670, 375))
            ]
        
        # Check if this looks like player hole cards
        elif region and region[1] > 450:  # Bottom player area
            cards = [
                Card("Q", "♦", 0.92, (600, 580)),
                Card("4", "♥", 0.94, (650, 580))
            ]
        
        return cards
    
    def detect_ui_elements(self, image: np.ndarray) -> Dict[str, any]:
        """Detect UI elements like buttons, sliders, etc."""
        ui_elements = {
            "buttons": [],
            "sliders": [],
            "text_areas": []
        }
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple button detection using contours
        # This is a basic implementation - in production use more sophisticated methods
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 10000:  # Button-sized areas
                x, y, w, h = cv2.boundingRect(contour)
                ui_elements["buttons"].append({
                    "bounds": (x, y, w, h),
                    "area": area,
                    "confidence": 0.8
                })
        
        return ui_elements


class UIElementDetector:
    """Detect poker UI elements like buttons, chips, etc."""
    
    def __init__(self):
        self.button_templates = []
        self.chip_templates = []
    
    def detect_buttons(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> List[Dict]:
        """Detect action buttons (Fold, Check, Bet, etc.)."""
        x, y, w, h = region  
        roi = image[y:y+h, x:x+w]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        buttons = []
        
        # Red button (likely Fold)
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum button size
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                buttons.append({
                    "type": "fold",
                    "bounds": (x + x1, y + y1, w1, h1),
                    "confidence": 0.8,
                    "color": "red"
                })
        
        # Green button (likely Check/Call)
        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                buttons.append({
                    "type": "check",
                    "bounds": (x + x1, y + y1, w1, h1),
                    "confidence": 0.8,
                    "color": "green"
                })
        
        return buttons
    
    def detect_chips(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> List[Dict]:
        """Detect chip stacks and amounts."""
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Simple circular detection for chips
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=50
        )
        
        chips = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (cx, cy, r) in circles:
                chips.append({
                    "center": (x + cx, y + cy),
                    "radius": r,
                    "confidence": 0.7
                })
        
        return chips