"""
Modern IDE Activity Bar for SoftWork PySide6 CAD IDE.
"""
from __future__ import annotations
from typing import Optional, Dict

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QFrame
    from PySide6.QtGui import QColor, QFont
except ImportError:
    pass


class QtActivityBar(QWidget):
    """
    Vertical icon strip on the left side of the IDE window.
    """
    tabChanged = Signal(str)
    settingsClicked = Signal()
    aiClicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(52)
        self.setStyleSheet("""
            QWidget {
                background-color: #080808;
                border-right: 1px solid #1C1C1C;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #888888;
                font-size: 16px;
                padding: 6px;
                min-height: 38px;
                min-width: 38px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                color: #00F0FF;
            }
            QPushButton:checked {
                background-color: #1F1F1F;
                color: #00F0FF;
                border-left: 2px solid #00F0FF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 10)
        layout.setSpacing(8)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Top Tabs
        self.btn_tree = QPushButton("📁")
        self.btn_tree.setToolTip("Model Feature Tree")
        self.btn_tree.setCheckable(True)
        self.btn_tree.setChecked(True)
        self.btn_group.addButton(self.btn_tree)
        layout.addWidget(self.btn_tree)

        self.btn_tools = QPushButton("🛠️")
        self.btn_tools.setToolTip("CAD Tools & Primitives")
        self.btn_tools.setCheckable(True)
        self.btn_group.addButton(self.btn_tools)
        layout.addWidget(self.btn_tools)

        self.btn_props = QPushButton("📊")
        self.btn_props.setToolTip("Properties Inspector")
        self.btn_props.setCheckable(True)
        self.btn_group.addButton(self.btn_props)
        layout.addWidget(self.btn_props)

        layout.addStretch()

        # Bottom Actions
        self.btn_ai = QPushButton("✨")
        self.btn_ai.setToolTip("Toggle Floating AI Copilot")
        self.btn_ai.setStyleSheet("color: #00F0FF;")
        self.btn_ai.clicked.connect(self.aiClicked.emit)
        layout.addWidget(self.btn_ai)

        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setToolTip("Workspace Settings")
        self.btn_settings.clicked.connect(self.settingsClicked.emit)
        layout.addWidget(self.btn_settings)

        self.btn_tree.clicked.connect(lambda: self.tabChanged.emit("tree"))
        self.btn_tools.clicked.connect(lambda: self.tabChanged.emit("tools"))
        self.btn_props.clicked.connect(lambda: self.tabChanged.emit("props"))
