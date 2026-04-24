#!/usr/bin/env python3
"""Main entry point."""

import sys
import os
from pathlib import Path

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).resolve().parent

src_path = base_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

os.chdir(base_path)


def main():
    from PyQt6.QtWidgets import QApplication
    from src.gui.window import MainWindow

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()