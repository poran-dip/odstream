#!/usr/bin/env python3
"""Build the frontend into frontend/dist, which the backend then serves."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
# Full path incl. extension on Windows (pnpm.cmd via corepack or pnpm.exe)
PNPM = shutil.which("pnpm") or "pnpm"


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, shell=False, check=False)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    if not (FRONTEND / "node_modules").exists():
        print("❌ Frontend dependencies not installed. Run setup.py first.")
        sys.exit(1)

    print("📦 Building frontend...")
    run([PNPM, "run", "build"], FRONTEND)
    print("✅ Build complete — run start.py to launch")
