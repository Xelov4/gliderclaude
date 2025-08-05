"""Data models for Poker AI MVP."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from enum import Enum


class GamePhase(Enum):
    """Game phases in poker."""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class Suit(Enum):
    """Card suits."""
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Rank(Enum):
    """Card ranks."""
    ACE = "A"
    KING = "K"
    QUEEN = "Q"
    JACK = "J"
    TEN = "10"
    NINE = "9"
    EIGHT = "8"
    SEVEN = "7" 
    SIX = "6"
    FIVE = "5"
    FOUR = "4"
    THREE = "3"
    TWO = "2"


@dataclass
class Card:
    """Represents a playing card."""
    rank: str
    suit: str
    confidence: float = 0.0
    position: Tuple[int, int] = (0, 0)
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
    
    def to_dict(self) -> Dict:
        return {
            "rank": self.rank,
            "suit": self.suit,
            "confidence": self.confidence,
            "position": self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Card":
        return cls(
            rank=data["rank"],
            suit=data["suit"],
            confidence=data.get("confidence", 0.0),
            position=tuple(data.get("position", (0, 0)))
        )


@dataclass
class Player:
    """Represents a player in the game."""
    position: int
    name: str
    stack_size: int
    hole_cards: List[Card] = field(default_factory=list)
    current_bet: int = 0
    is_active: bool = True
    is_current: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position,
            "name": self.name,
            "stack_size": self.stack_size,
            "hole_cards": [card.to_dict() for card in self.hole_cards],
            "current_bet": self.current_bet,
            "is_active": self.is_active,
            "is_current": self.is_current
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        return cls(
            position=data["position"],
            name=data["name"],
            stack_size=data["stack_size"],
            hole_cards=[Card.from_dict(card) for card in data.get("hole_cards", [])],
            current_bet=data.get("current_bet", 0),
            is_active=data.get("is_active", True),
            is_current=data.get("is_current", False)
        )


@dataclass
class GameState:
    """Represents complete game state at a point in time."""
    timestamp: datetime
    hand_id: str
    game_phase: GamePhase
    pot_size: int
    community_cards: List[Card] = field(default_factory=list)
    players: List[Player] = field(default_factory=list)
    timer_remaining: int = 0
    available_actions: List[str] = field(default_factory=list)
    betting_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "hand_id": self.hand_id,
            "game_phase": self.game_phase.value,
            "pot_size": self.pot_size,
            "community_cards": [card.to_dict() for card in self.community_cards],
            "players": [player.to_dict() for player in self.players],
            "timer_remaining": self.timer_remaining,
            "available_actions": self.available_actions,
            "betting_options": self.betting_options
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "GameState":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            hand_id=data["hand_id"],
            game_phase=GamePhase(data["game_phase"]),
            pot_size=data["pot_size"],
            community_cards=[Card.from_dict(card) for card in data.get("community_cards", [])],
            players=[Player.from_dict(player) for player in data.get("players", [])],
            timer_remaining=data.get("timer_remaining", 0),
            available_actions=data.get("available_actions", []),
            betting_options=data.get("betting_options", {})
        )


@dataclass
class VisionMetrics:
    """Vision processing performance metrics."""
    timestamp: datetime
    processing_time_ms: int
    frame_rate: float
    card_detection_confidence: float
    text_ocr_confidence: float
    elements_detected: int
    elements_failed: int
    error_details: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "frame_rate": self.frame_rate,
            "card_detection_confidence": self.card_detection_confidence,
            "text_ocr_confidence": self.text_ocr_confidence,
            "elements_detected": self.elements_detected,
            "elements_failed": self.elements_failed,
            "error_details": self.error_details
        }


@dataclass 
class SessionInfo:
    """Information about a poker session."""
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_hands: int = 0
    total_frames_processed: int = 0
    status: str = "active"  # active, paused, completed
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_hands": self.total_hands,
            "total_frames_processed": self.total_frames_processed,
            "status": self.status
        }