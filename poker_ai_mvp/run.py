#!/usr/bin/env python3
"""
Poker AI MVP - Run Script

Simple script to run the Poker AI vision system.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.main import main

if __name__ == "__main__":
    main()