"""Basic tests for Poker AI MVP components."""
import pytest
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.data.models import Card, Player, GameState, GamePhase
from src.data.database import DatabaseManager
from src.vision.capture import ScreenCapture


class TestDataModels:
    """Test data models."""
    
    def test_card_creation(self):
        """Test card model creation."""
        card = Card("A", "♠", 0.95, (100, 200))
        assert card.rank == "A"
        assert card.suit == "♠"
        assert card.confidence == 0.95
        assert card.position == (100, 200)
        assert str(card) == "A♠"
    
    def test_card_serialization(self):
        """Test card to/from dict conversion."""
        card = Card("K", "♥", 0.9, (150, 250))
        card_dict = card.to_dict()
        
        assert card_dict["rank"] == "K"
        assert card_dict["suit"] == "♥"
        assert card_dict["confidence"] == 0.9
        assert card_dict["position"] == (150, 250)
        
        # Test reconstruction
        card2 = Card.from_dict(card_dict)
        assert card2.rank == card.rank
        assert card2.suit == card.suit
        assert card2.confidence == card.confidence
        assert card2.position == card.position
    
    def test_player_creation(self):
        """Test player model creation."""
        cards = [Card("A", "♠", 0.9, (100, 100)), Card("K", "♥", 0.9, (150, 100))]
        player = Player(0, "TestPlayer", 1000, cards, 50, True, False)
        
        assert player.position == 0
        assert player.name == "TestPlayer"
        assert player.stack_size == 1000
        assert len(player.hole_cards) == 2
        assert player.current_bet == 50
        assert player.is_active is True
        assert player.is_current is False
    
    def test_game_state_creation(self):
        """Test game state model creation."""
        timestamp = datetime.now()
        community_cards = [Card("A", "♠", 0.9, (100, 100))]
        players = [Player(0, "Player1", 1000)]
        
        game_state = GameState(
            timestamp=timestamp,
            hand_id="test_hand_001",
            game_phase=GamePhase.FLOP,
            pot_size=100,
            community_cards=community_cards,
            players=players,
            timer_remaining=60,
            available_actions=["fold", "call", "raise"],
            betting_options={"min": 10, "max": 100}
        )
        
        assert game_state.hand_id == "test_hand_001"
        assert game_state.game_phase == GamePhase.FLOP
        assert game_state.pot_size == 100
        assert len(game_state.community_cards) == 1
        assert len(game_state.players) == 1
        assert "fold" in game_state.available_actions


class TestDatabase:
    """Test database operations."""
    
    def test_database_creation(self):
        """Test database initialization."""
        # Use temporary database
        db = DatabaseManager(":memory:")
        assert db is not None
    
    def test_session_creation(self):
        """Test session creation."""
        db = DatabaseManager(":memory:")
        session_id = db.create_session()
        assert isinstance(session_id, int)
        assert session_id > 0
    
    def test_game_state_storage(self):
        """Test game state storage and retrieval."""
        db = DatabaseManager(":memory:")
        session_id = db.create_session()
        
        # Create test game state
        timestamp = datetime.now()
        game_state = GameState(
            timestamp=timestamp,
            hand_id="test_hand_002",
            game_phase=GamePhase.PREFLOP,
            pot_size=50,
            community_cards=[],
            players=[Player(0, "TestPlayer", 1000)],
            timer_remaining=30,
            available_actions=["fold", "call"],
            betting_options={}
        )
        
        # Save game state
        game_state_id = db.save_game_state(game_state, session_id)
        assert isinstance(game_state_id, int)
        assert game_state_id > 0


class TestScreenCapture:
    """Test screen capture functionality."""
    
    def test_screen_capture_init(self):
        """Test screen capture initialization."""
        capture = ScreenCapture()
        assert capture is not None
        assert capture.fps_target == 30
        assert capture.running is False
    
    def test_performance_stats(self):
        """Test performance statistics."""
        capture = ScreenCapture()
        stats = capture.get_performance_stats()
        
        assert "current_fps" in stats
        assert "target_fps" in stats
        assert "frames_captured" in stats
        assert "is_running" in stats
        
        assert stats["target_fps"] == 30
        assert stats["is_running"] is False


class TestIntegration:
    """Integration tests."""
    
    def test_full_pipeline_mock(self):
        """Test full pipeline with mock data."""
        # This would test the complete flow:
        # Screen capture -> Vision processing -> Data storage -> Dashboard update
        
        # For now, just verify components can be instantiated together
        db = DatabaseManager(":memory:")
        capture = ScreenCapture()
        
        session_id = db.create_session()
        assert session_id > 0
        
        # Mock game state
        game_state = GameState(
            timestamp=datetime.now(),
            hand_id="integration_test",
            game_phase=GamePhase.FLOP,
            pot_size=100,
            community_cards=[Card("A", "♠", 0.9, (100, 100))],
            players=[Player(0, "IntegrationTest", 1000)],
            timer_remaining=45,
            available_actions=["fold", "call", "raise"],
            betting_options={"min": 10}
        )
        
        # Store in database
        game_state_id = db.save_game_state(game_state, session_id)
        assert game_state_id > 0
        
        # Verify session stats
        stats = db.get_session_stats(session_id)
        assert stats["session_id"] == session_id
        assert stats["total_hands"] >= 1


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main(["-v", __file__])