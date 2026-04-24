"""Build script using Nuitka for cross-platform compilation."""

import subprocess
import sys
import platform
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "dist"


def build_windows():
    """Build Windows executable."""
    print("Building for Windows...")
    subprocess.run([
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-disable-console",
        f"--include-data-dir={SRC_DIR};src",
        f"--output-dir={OUTPUT_DIR}",
        str(PROJECT_ROOT / "main.py"),
    ], check=True)


def build_macos():
    """Build macOS executable."""
    print("Building for macOS...")
    subprocess.run([
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--macos-disable-console",
        f"--include-data-dir={SRC_DIR}:src",
        f"--output-dir={OUTPUT_DIR}",
        str(PROJECT_ROOT / "main.py"),
    ], check=True)


def build_linux():
    """Build Linux executable."""
    print("Building for Linux...")
    subprocess.run([
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--linux-disable-console",
        f"--include-data-dir={SRC_DIR}:src",
        f"--output-dir={OUTPUT_DIR}",
        str(PROJECT_ROOT / "main.py"),
    ], check=True)


def build():
    """Main build function."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    system = platform.system()
    
    if system == "Windows":
        build_windows()
    elif system == "Darwin":
        build_macos()
    else:
        build_linux()
    
    print(f"Build complete. Output in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()