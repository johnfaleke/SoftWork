"""
SoftWork Qt6 Modern CAD IDE Bootstrap Entry Point.
"""
from __future__ import annotations
import sys

from softwork.core.document import Document
from softwork.qt.main_window import CADMainWindow

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    pass


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("SoftWork")
    app.setOrganizationName("SoftWork CAD")

    doc = Document(name="Untitled.softwork")
    window = CADMainWindow(doc)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
