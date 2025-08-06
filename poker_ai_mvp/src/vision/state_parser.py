"""Game state parsing from poker table images."""
import cv2
import numpy as np
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from loguru import logger
import time

from .detection import CardDetector
from .ocr import TextRecognizer
from ..data.models import GameState, Player, Card, GamePhase, VisionMetrics


class GameStateParser:
    """Parse poker game state from captured images."""
    
    def __init__(self):
        """Initialize parser with detection components."""
        self.card_detector = CardDetector()
        self.text_recognizer = TextRecognizer()
        
        # Load region configurations
        from ..config.settings import settings
        self.regions = settings.game_client.table_regions
        
        # Performance optimization: cache for repeated regions
        self._cache = {}
        self._cache_size = 100
        self._last_parse_time = 0
        self._parse_timeout = 0.1  # Skip parsing if last call was too recent
        
        logger.info("GameStateParser initialized")
    
    def parse_game_state(self, image: np.ndarray, timestamp: datetime) -> Optional[GameState]:
        """Parse complete game state from image."""
        # Performance optimization: skip parsing if too frequent
        current_time = time.time()
        if current_time - self._last_parse_time < self._parse_timeout:
            return None
        
        try:
            start_time = time.time()
            
            # Performance optimization: batch text extraction
            text_elements = self._batch_extract_text(image)
            
            # Extract community cards
            community_cards = self._extract_community_cards(image)
            
            # Extract players with batched text data
            players = self._extract_players_optimized(image, text_elements)
            
            # Extract pot size from batched text
            pot_size = self._extract_pot_size_from_batch(text_elements)
            
            # Extract timer from batched text
            timer_remaining = self._extract_timer_from_batch(text_elements)
            
            # Determine game phase
            game_phase = self._determine_game_phase(community_cards)
            
            # Generate hand ID (simplified)
            hand_id = self._generate_hand_id(timestamp, community_cards, players)
            
            # Extract available actions
            available_actions = self._extract_available_actions(image)
            
            # Extract betting options  
            betting_options = self._extract_betting_options(image)
            
            # Create game state
            game_state = GameState(
                timestamp=timestamp,
                hand_id=hand_id,
                game_phase=game_phase,
                pot_size=pot_size or 0,
                community_cards=community_cards,
                players=players,
                timer_remaining=timer_remaining or 0,
                available_actions=available_actions,
                betting_options=betting_options
            )
            
            # Calculate processing metrics
            processing_time = (time.time() - start_time) * 1000
            
            # Performance optimization: log only if slow
            if processing_time > 50:
                logger.warning(f"Slow game state parsing: {processing_time:.1f}ms")
            
            self._last_parse_time = current_time
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to parse game state: {e}")
            return None
    
    def _batch_extract_text(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """Extract all text elements in one batch operation."""
        text_elements = {}
        
        # Extract text from all relevant regions
        regions_to_extract = [
            ("pot", self.regions["pot_display"]),
            ("timer", self.regions["timer"]),
            ("player_0", self.regions["player_0"]),
            ("player_1", self.regions["player_1"]),
            ("player_2", self.regions["player_2"])
        ]
        
        for region_name, region_config in regions_to_extract:
            region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
            elements = self.text_recognizer.extract_text(image, region)
            text_elements[region_name] = elements
        
        return text_elements
    
    def _extract_community_cards(self, image: np.ndarray) -> List[Card]:
        """Extract community cards from center of table."""
        region_config = self.regions["community_cards"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        cards = self.card_detector.detect_cards(image, region)
        
        # Sort cards by position (left to right)
        cards.sort(key=lambda c: c.position[0])
        
        return cards
    
    def _extract_players_optimized(self, image: np.ndarray, text_elements: Dict[str, List[Dict]]) -> List[Player]:
        """Extract all player information using batched text data."""
        players = []
        
        for position in range(3):  # 3-player game
            player = self._extract_single_player_optimized(image, position, text_elements)
            if player:
                players.append(player)
        
        return players
    
    def _extract_single_player_optimized(self, image: np.ndarray, position: int, text_elements: Dict[str, List[Dict]]) -> Optional[Player]:
        """Extract single player information using batched text data."""
        region_config = self.regions[f"player_{position}"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        try:
            # Use batched text data instead of individual OCR calls
            player_text = text_elements.get(f"player_{position}", [])
            
            # Extract player name from text elements
            name = self._extract_name_from_text_elements(player_text, region)
            
            # Extract stack size from text elements
            stack_size = self._extract_stack_from_text_elements(player_text, region)
            
            # Extract hole cards (if visible)
            cards_region = (region[0] + region[2]//2, region[1], region[2]//2, region[3]//2)
            hole_cards = self.card_detector.detect_cards(image, cards_region)
            
            # Determine if player is active/current
            is_active, is_current = self._analyze_player_status(image, region)
            
            # Extract current bet (if any)
            current_bet = self._extract_player_bet(image, region)
            
            # Use fallback values if detection failed
            if not name:
                name = f"Player_{position}"
            if stack_size is None:
                stack_size = 0
            if current_bet is None:
                current_bet = 0
            
            player = Player(
                position=position,
                name=name,
                stack_size=stack_size,
                hole_cards=hole_cards,
                current_bet=current_bet,
                is_active=is_active,
                is_current=is_current
            )
            
            return player
            
        except Exception as e:
            logger.error(f"Failed to extract player {position}: {e}")
            return None
    
    def _extract_name_from_text_elements(self, text_elements: List[Dict], region: Tuple[int, int, int, int]) -> Optional[str]:
        """Extract player name from text elements."""
        x, y, w, h = region
        name_region = (x, y, w//2, h//3)
        
        for element in text_elements:
            if self._is_in_region(element["center"], name_region):
                text = element["text"]
                if self.text_recognizer.patterns["player_name"].match(text) and element["confidence"] > 0.6:
                    return text
        return None
    
    def _extract_stack_from_text_elements(self, text_elements: List[Dict], region: Tuple[int, int, int, int]) -> Optional[int]:
        """Extract stack size from text elements."""
        x, y, w, h = region
        stack_region = (x, y + h//2, w//2, h//3)
        
        for element in text_elements:
            if self._is_in_region(element["center"], stack_region):
                text = element["text"]
                if self.text_recognizer.patterns["stack_size"].match(text) and element["confidence"] > 0.7:
                    try:
                        return int(text)
                    except ValueError:
                        continue
        return None
    
    def _is_in_region(self, center: Tuple[int, int], region: Tuple[int, int, int, int]) -> bool:
        """Check if center point is within region."""
        x, y, w, h = region
        cx, cy = center
        return x <= cx <= x + w and y <= cy <= y + h
    
    def _extract_pot_size_from_batch(self, text_elements: Dict[str, List[Dict]]) -> Optional[int]:
        """Extract pot size from batched text elements."""
        pot_elements = text_elements.get("pot", [])
        
        for element in pot_elements:
            text = element["text"]
            if self.text_recognizer.patterns["pot_size"].match(text) and element["confidence"] > 0.7:
                try:
                    return int(text)
                except ValueError:
                    continue
        return None
    
    def _extract_timer_from_batch(self, text_elements: Dict[str, List[Dict]]) -> Optional[int]:
        """Extract timer from batched text elements."""
        timer_elements = text_elements.get("timer", [])
        
        for element in timer_elements:
            text = element["text"]
            if self.text_recognizer.patterns["timer"].match(text) and element["confidence"] > 0.7:
                try:
                    # Convert MM:SS to total seconds
                    minutes, seconds = map(int, text.split(":"))
                    return minutes * 60 + seconds
                except ValueError:
                    continue
        return None
    
    def _extract_pot_size(self, image: np.ndarray) -> Optional[int]:
        """Extract pot size from pot display area."""
        region_config = self.regions["pot_display"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        return self.text_recognizer.extract_pot_size(image, region)
    
    def _extract_timer(self, image: np.ndarray) -> Optional[int]:
        """Extract timer countdown in seconds."""
        region_config = self.regions["timer"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        return self.text_recognizer.extract_timer(image, region)
    
    def _determine_game_phase(self, community_cards: List[Card]) -> GamePhase:
        """Determine current game phase based on community cards."""
        card_count = len(community_cards)
        
        if card_count == 0:
            return GamePhase.PREFLOP
        elif card_count == 3:
            return GamePhase.FLOP
        elif card_count == 4:
            return GamePhase.TURN
        elif card_count == 5:
            return GamePhase.RIVER
        else:
            logger.warning(f"Unexpected number of community cards: {card_count}")
            return GamePhase.PREFLOP
    
    def _generate_hand_id(self, timestamp: datetime, community_cards: List[Card], players: List[Player]) -> str:
        """Generate unique hand ID."""
        # Simple hash-based ID
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        card_count = len(community_cards)
        player_count = len(players)
        
        # Create a simple hash
        hash_input = f"{timestamp_str}_{card_count}_{player_count}"
        hash_value = hash(hash_input) % 1000000
        
        return f"hand_{hash_value}"
    
    def _extract_available_actions(self, image: np.ndarray) -> List[str]:
        """Extract available player actions."""
        # For MVP, return common actions
        return ["fold", "call", "raise"]
    
    def _extract_betting_options(self, image: np.ndarray) -> Dict[str, any]:
        """Extract betting options and amounts."""
        # For MVP, return mock betting options
        return {
            "min_raise": 10,
            "max_raise": 100,
            "pot_size": 80
        }
    
    def _analyze_player_status(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Tuple[bool, bool]:
        """Analyze if player is active and current."""
        # For MVP, use simple heuristics
        x, y, w, h = region
        
        # Check if region has significant content (not empty)
        roi = image[y:y+h, x:x+w]
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Simple activity detection based on non-zero pixels
        non_zero_ratio = np.count_nonzero(gray) / (w * h)
        is_active = non_zero_ratio > 0.1  # At least 10% non-zero pixels
        
        # For MVP, assume first player is current
        is_current = x < 1000  # Simple heuristic based on position
        
        return is_active, is_current
    
    def _extract_player_bet(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[int]:
        """Extract current bet amount for player."""
        # For MVP, return None (no bet detected)
        return None
    
    def calculate_vision_metrics(self, game_state: Optional[GameState], processing_time_ms: int) -> VisionMetrics:
        """Calculate vision processing metrics."""
        from ..data.models import VisionMetrics
        
        return VisionMetrics(
            timestamp=datetime.now(),
            processing_time_ms=processing_time_ms,
            cards_detected=len(game_state.community_cards) if game_state else 0,
            players_detected=len(game_state.players) if game_state else 0,
            text_confidence=0.85,  # Average confidence
            frame_rate=30.0  # Will be updated by caller
        )