"""
SoftWork Application entry point.
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
from softwork.ui.main_window import MainWindow


def main() -> None:
    parser = argparse.ArgumentParser(description="SoftWork — AI-native Parametric CAD")
    parser.add_argument("file", nargs="?", help="Optional .softwork document file to open")
    parser.add_argument("--demo", action="store_true", help="Launch directly into demo flow")
    args = parser.parse_args()

    doc = None
    if args.file:
        from softwork.document.serializer import load_document
        doc = load_document(args.file)

    app = MainWindow(document=doc)
    if args.demo:
        app.after(500, app._action_run_demo_flow)
    app.mainloop()


if __name__ == "__main__":
    main()
