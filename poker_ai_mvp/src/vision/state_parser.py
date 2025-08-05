"""Game state parsing and reconstruction."""
import cv2
import numpy as np
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from loguru import logger

from ..data.models import GameState, Player, Card, GamePhase, VisionMetrics
from ..config.settings import settings
from .detection import CardDetector, UIElementDetector
from .ocr import TextRecognizer


class GameStateParser:
    """Parse complete game state from poker client screenshot."""
    
    def __init__(self):
        self.card_detector = CardDetector()
        self.ui_detector = UIElementDetector()
        self.text_recognizer = TextRecognizer()
        
        # Game client regions from settings
        self.regions = settings.game_client.table_regions
        
        # State tracking
        self.last_hand_id = None
        self.hand_counter = 0
        
        logger.info("GameStateParser initialized")
    
    def parse_game_state(self, image: np.ndarray, timestamp: datetime) -> Optional[GameState]:
        """Parse complete game state from screenshot."""
        start_time = datetime.now()
        
        try:
            # Extract community cards
            community_cards = self._extract_community_cards(image)
            
            # Extract players
            players = self._extract_players(image)
            
            # Extract pot size
            pot_size = self._extract_pot_size(image)
            
            # Extract timer
            timer_remaining = self._extract_timer(image)
            
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
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.debug(f"Game state parsed in {processing_time:.1f}ms")
            
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to parse game state: {e}")
            return None
    
    def _extract_community_cards(self, image: np.ndarray) -> List[Card]:
        """Extract community cards from center of table."""
        region_config = self.regions["community_cards"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        cards = self.card_detector.detect_cards(image, region)
        
        # Sort cards by position (left to right)
        cards.sort(key=lambda c: c.position[0])
        
        logger.debug(f"Detected {len(cards)} community cards")
        return cards
    
    def _extract_players(self, image: np.ndarray) -> List[Player]:
        """Extract all player information."""
        players = []
        
        for position in range(3):  # 3-player game
            player = self._extract_single_player(image, position)
            if player:
                players.append(player)
        
        logger.debug(f"Extracted {len(players)} players")
        return players
    
    def _extract_single_player(self, image: np.ndarray, position: int) -> Optional[Player]:
        """Extract single player information."""
        region_config = self.regions[f"player_{position}"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        try:
            # Extract player name
            name_region = (region[0], region[1], region[2]//2, region[3]//3)
            name = self.text_recognizer.extract_player_name(image, name_region)
            
            # Extract stack size
            stack_region = (region[0], region[1] + region[3]//2, region[2]//2, region[3]//3)
            stack_size = self.text_recognizer.extract_stack_size(image, stack_region)
            
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
    
    def _extract_pot_size(self, image: np.ndarray) -> Optional[int]:
        """Extract pot size from center display."""
        region_config = self.regions["pot_display"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        return self.text_recognizer.extract_pot_size(image, region)
    
    def _extract_timer(self, image: np.ndarray) -> Optional[int]:
        """Extract countdown timer."""
        region_config = self.regions["timer"]
        region = (region_config["x"], region_config["y"], region_config["w"], region_config["h"])
        
        return self.text_recognizer.extract_timer(image, region)
    
    def _determine_game_phase(self, community_cards: List[Card]) -> GamePhase:
        """Determine game phase based on community cards."""
        num_cards = len(community_cards)
        
        if num_cards == 0:
            return GamePhase.PREFLOP
        elif num_cards == 3:
            return GamePhase.FLOP
        elif num_cards == 4:
            return GamePhase.TURN
        elif num_cards == 5:
            return GamePhase.RIVER
        else:
            logger.warning(f"Unexpected number of community cards: {num_cards}")
            return GamePhase.PREFLOP
    
    def _generate_hand_id(self, timestamp: datetime, community_cards: List[Card], players: List[Player]) -> str:
        """Generate unique hand identifier."""
        # Simple hand ID based on timestamp and card hash
        cards_str = "".join([str(card) for card in community_cards])
        players_str = "".join([p.name for p in players])
        
        hash_input = f"{timestamp.isoformat()}{cards_str}{players_str}"
        hand_id = f"hand_{abs(hash(hash_input)) % 1000000:06d}"
        
        # Check if this is a new hand
        if hand_id != self.last_hand_id:
            self.hand_counter += 1
            self.last_hand_id = hand_id
        
        return hand_id
    
    def _extract_available_actions(self, image: np.ndarray) -> List[str]:
        """Extract available action buttons."""
        # Look for action buttons in bottom area
        action_region = (400, 600, 800, 200)  # Bottom center area
        buttons = self.ui_detector.detect_buttons(image, action_region)
        
        actions = []
        for button in buttons:
            if button["type"] in ["fold", "check", "call", "bet", "raise"]:
                actions.append(button["type"])
        
        # Fallback actions
        if not actions:
            actions = ["fold", "check", "bet"]
        
        return actions
    
    def _extract_betting_options(self, image: np.ndarray) -> Dict[str, any]:
        """Extract betting slider options."""
        # Look for betting controls
        betting_region = (800, 550, 400, 150)  # Right side betting area
        
        # For MVP, return default betting options
        betting_options = {
            "min_bet": 20,
            "max_bet": 1000,
            "slider_positions": {
                "35%": 35,
                "65%": 65,
                "pot": 100,
                "all_in": 200
            }
        }
        
        return betting_options
    
    def _analyze_player_status(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Tuple[bool, bool]:
        """Analyze if player is active and current to act."""
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Look for highlighting or special indicators
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Check for yellow/gold highlighting (current player)
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        is_current = np.sum(yellow_mask) > 1000  # Threshold for highlighting
        
        # Check for grayed out (inactive player)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        is_active = avg_brightness > 50  # Threshold for active vs folded
        
        return is_active, is_current
    
    def _extract_player_bet(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[int]:
        """Extract current bet amount for player."""
        # Look for bet chips or text near player
        x, y, w, h = region
        bet_region = (x - 50, y + h//2, 100, 50)  # Area in front of player
        
        # Try to extract bet amount
        bet_amount = self.text_recognizer.extract_stack_size(image, bet_region)
        
        return bet_amount if bet_amount else 0
    
    def calculate_vision_metrics(self, game_state: Optional[GameState], processing_time_ms: int) -> VisionMetrics:
        """Calculate vision processing performance metrics."""
        timestamp = datetime.now()
        
        if game_state:
            # Count successful detections
            cards_detected = len(game_state.community_cards)
            players_detected = len(game_state.players)
            total_elements = cards_detected + players_detected + (1 if game_state.pot_size > 0 else 0)
            
            # Calculate confidence scores
            card_confidences = [card.confidence for card in game_state.community_cards]
            avg_card_confidence = sum(card_confidences) / len(card_confidences) if card_confidences else 0.0
            
            # Estimate OCR confidence (simplified)
            ocr_confidence = 0.9 if game_state.pot_size > 0 else 0.0
            
            elements_failed = 0
            error_details = []
        else:
            total_elements = 0
            avg_card_confidence = 0.0
            ocr_confidence = 0.0
            elements_failed = 1
            error_details = ["Failed to parse game state"]
        
        return VisionMetrics(
            timestamp=timestamp,
            processing_time_ms=processing_time_ms,
            frame_rate=0.0,  # Will be calculated by capture module
            card_detection_confidence=avg_card_confidence,
            text_ocr_confidence=ocr_confidence,
            elements_detected=total_elements,
            elements_failed=elements_failed,
            error_details=error_details
        )