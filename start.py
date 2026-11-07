#!/usr/bin/env python3
"""Start the backend (which also serves the built frontend, see build.py)."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND = ROOT / "backend"
PYTHON = (
    BACKEND / "venv" / "Scripts" / "python.exe"
    if sys.platform == "win32"
    else BACKEND / "venv" / "bin" / "python"
)


if __name__ == "__main__":
    if not PYTHON.exists():
        print("❌ Virtual environment not found. Run setup.py first.")
        sys.exit(1)

    print("🚀 Starting backend...")
    try:
        subprocess.run([str(PYTHON), "app.py"], cwd=BACKEND, check=False)
    except KeyboardInterrupt:
        print("\n👋 App closed")
        sys.exit(0)
