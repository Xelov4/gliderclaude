"""Configuration settings for Poker AI MVP."""
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field


class ScreenCaptureConfig(BaseModel):
    """Screen capture configuration."""
    monitor: int = 0
    fps: int = 30
    region: Dict[str, int] = Field(default_factory=lambda: {
        "x": 0, "y": 0, "width": 1920, "height": 1080
    })


class VisionConfig(BaseModel):
    """Vision processing configuration."""
    card_detection: Dict[str, Any] = Field(default_factory=lambda: {
        "model_path": "models/yolov9_cards.pt",
        "confidence_threshold": 0.8,
        "nms_threshold": 0.4
    })
    text_recognition: Dict[str, Any] = Field(default_factory=lambda: {
        "ocr_language": "en",
        "confidence_threshold": 0.7
    })


class DatabaseConfig(BaseModel):
    """Database configuration."""
    path: str = "data/poker_vision.db"
    backup_frequency: int = 3600  # seconds
    retention_days: int = 30


class DashboardConfig(BaseModel):
    """Dashboard configuration."""
    update_frequency_ms: int = 100
    max_log_entries: int = 1000
    auto_scroll: bool = True


class GameClientConfig(BaseModel):
    """Game client specific configuration."""
    window_title: str = "Poker Client"
    table_regions: Dict[str, Dict[str, int]] = Field(default_factory=lambda: {
        "community_cards": {"x": 530, "y": 315, "w": 270, "h": 120},
        "pot_display": {"x": 810, "y": 260, "w": 100, "h": 40},
        "timer": {"x": 1160, "y": 60, "w": 100, "h": 40},
        "player_0": {"x": 475, "y": 500, "w": 350, "h": 200},
        "player_1": {"x": 250, "y": 200, "w": 350, "h": 200},
        "player_2": {"x": 900, "y": 200, "w": 350, "h": 200}
    })


class Settings(BaseModel):
    """Main settings configuration."""
    screen_capture: ScreenCaptureConfig = Field(default_factory=ScreenCaptureConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    game_client: GameClientConfig = Field(default_factory=GameClientConfig)

    @classmethod
    def load_from_file(cls, file_path: str) -> "Settings":
        """Load settings from JSON file."""
        path = Path(file_path)
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            return cls(**data)
        else:
            # Create default settings file
            settings = cls()
            settings.save_to_file(file_path)
            return settings

    def save_to_file(self, file_path: str) -> None:
        """Save settings to JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)


# Global settings instance
settings = Settings.load_from_file("config/settings.json")