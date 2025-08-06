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

try:
    from src.main import main
except ImportError as e:
    print("❌ Import Error:")
    print(f"   {e}")
    print("\n💡 Solutions:")
    print("   1. Run: setup_python.bat")
    print("   2. Activate venv: venv\\Scripts\\activate.bat")
    print("   3. Install deps: pip install -r requirements.txt")
    input("\nPress Enter to exit...")
    exit(1)

if __name__ == "__main__":
    main()