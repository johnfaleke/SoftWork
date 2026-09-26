"""
SoftWork Application entry point.
Launches the modern PySide6 / Qt6 CAD IDE by default with graceful fallback to Tkinter.
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path

# Automatically add src directory to sys.path if not present
_src_dir = Path(__file__).resolve().parent.parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from softwork.core.document import Document


def main() -> None:
    parser = argparse.ArgumentParser(description="SoftWork — AI-native Parametric CAD IDE")
    parser.add_argument("file", nargs="?", help="Optional .softwork document file to open")
    parser.add_argument("--demo", action="store_true", help="Launch directly into demo flow")
    parser.add_argument("--legacy-tk", action="store_true", help="Force legacy Tkinter UI")
    args = parser.parse_args()

    doc = None
    if args.file:
        from softwork.document.serializer import load_document
        doc = load_document(args.file)

    # 1. Prefer Modern PySide6 / Qt6 CAD IDE
    if not args.legacy_tk:
        try:
            from PySide6.QtWidgets import QApplication
            from softwork.qt.main_window import CADMainWindow

            app = QApplication(sys.argv)
            app.setApplicationName("SoftWork CAD")
            app.setOrganizationName("SoftWork")

            window = CADMainWindow(document=doc)
            window.show()

            if args.demo:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(500, window._action_demo_flow)

            sys.exit(app.exec())
        except ImportError:
            pass

    # 2. Fallback to Tkinter UI if PySide6 is not requested or unavailable
    from softwork.ui.main_window import MainWindow
    tk_app = MainWindow(document=doc)
    if args.demo:
        tk_app.after(500, tk_app._action_run_demo_flow)
    tk_app.mainloop()


if __name__ == "__main__":
    main()
