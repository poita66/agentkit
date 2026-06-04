"""Standalone database initialization module.

Usage: python -m backend.src.db.init
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.src.db.session import init_db


def main():
    asyncio.run(init_db())
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
