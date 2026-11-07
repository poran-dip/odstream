#!/usr/bin/env python3
"""One-time setup: backend venv + Python deps, OpenH264 (Windows), frontend deps.

Run order: setup.py -> build.py -> start.py
"""

import bz2
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / "venv"
PIP = VENV / "Scripts" / "pip.exe" if sys.platform == "win32" else VENV / "bin" / "pip"
# Full path incl. extension on Windows (pnpm.cmd via corepack or pnpm.exe)
PNPM = shutil.which("pnpm") or "pnpm"


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, shell=False, check=False)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)


def download_openh264():
    dll_name = "openh264-2.5.0-win64.dll"
    dll_path = BACKEND / dll_name

    if dll_path.exists():
        print("✅ OpenH264 already present, skipping")
        return

    url = f"http://ciscobinary.openh264.org/{dll_name}.bz2"
    bz2_path = BACKEND / f"{dll_name}.bz2"

    print(f"📥 Downloading {dll_name}...")
    urllib.request.urlretrieve(url, bz2_path)

    with bz2.open(bz2_path, "rb") as f_in, open(dll_path, "wb") as f_out:
        f_out.write(f_in.read())

    bz2_path.unlink()
    print(f"✅ OpenH264 extracted to {dll_path}")


if __name__ == "__main__":
    # Backend venv
    if not VENV.exists():
        print("🐍 Creating virtual environment...")
        run([sys.executable, "-m", "venv", "venv"], BACKEND)
        print("📦 Installing Python dependencies...")
        run([str(PIP), "install", "-r", "requirements.txt"], BACKEND)
    else:
        print("✅ Virtual environment already exists, skipping")

    # OpenH264 (Windows only)
    if sys.platform == "win32":
        download_openh264()

    # Frontend deps
    print("📦 Installing frontend dependencies...")
    run([PNPM, "install"], FRONTEND)

    print("\n✅ Setup complete — run build.py next")
