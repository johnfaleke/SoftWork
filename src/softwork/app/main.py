"""
SoftWork Application entry point.
"""
from __future__ import annotations
import sys
import argparse

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
