"""
Professional CAD Sidebar Activity Bar for SoftWork (PTC Creo & SolidWorks aesthetic).
"""
from __future__ import annotations
from typing import Optional

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QFrame
    from PySide6.QtGui import QColor, QFont
except ImportError:
    pass


class QtActivityBar(QWidget):
    """
    Vertical icon strip on the left side of the CAD window.
    Provides rapid switching between Feature Tree, Tools, Properties, Copilot, and Settings.
    """
    tabChanged = Signal(str)
    settingsClicked = Signal()
    aiClicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(56)
        self.setStyleSheet("""
            QWidget {
                background-color: #181A1F;
                border-right: 1px solid #2C313A;
            }
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                color: #8B949E;
                font-family: "Segoe UI", "Tahoma", sans-serif;
                font-size: 9px;
                font-weight: 700;
                padding: 4px 2px;
                min-height: 28px;
                min-width: 48px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #282C34;
                color: #00A8FF;
                border: 1px solid #3E4451;
            }
            QPushButton:checked {
                background-color: #21252B;
                color: #00A8FF;
                border: 1px solid #00A8FF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(6)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Top Tabs
        self.btn_tree = QPushButton("Tree")
        self.btn_tree.setToolTip("FeatureManager Design Tree")
        self.btn_tree.setCheckable(True)
        self.btn_tree.setChecked(True)
        self.btn_group.addButton(self.btn_tree)
        layout.addWidget(self.btn_tree)

        self.btn_tools = QPushButton("Features")
        self.btn_tools.setToolTip("Parametric Features and Primitives")
        self.btn_tools.setCheckable(True)
        self.btn_group.addButton(self.btn_tools)
        layout.addWidget(self.btn_tools)

        self.btn_props = QPushButton("Properties")
        self.btn_props.setToolTip("PropertyManager and Parameters")
        self.btn_props.setCheckable(True)
        self.btn_group.addButton(self.btn_props)
        layout.addWidget(self.btn_props)

        layout.addStretch()

        # Bottom Actions
        self.btn_ai = QPushButton("Copilot")
        self.btn_ai.setToolTip("Parametric Copilot HUD")
        self.btn_ai.setStyleSheet("""
            QPushButton {
                color: #00A8FF;
                border: 1px solid #007ACC;
                background-color: #1E2227;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #007ACC;
                color: #FFFFFF;
            }
        """)
        self.btn_ai.clicked.connect(self.aiClicked.emit)
        layout.addWidget(self.btn_ai)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setToolTip("Workspace and Units Configuration")
        self.btn_settings.clicked.connect(self.settingsClicked.emit)
        layout.addWidget(self.btn_settings)

        self.btn_tree.clicked.connect(lambda: self.tabChanged.emit("tree"))
        self.btn_tools.clicked.connect(lambda: self.tabChanged.emit("tools"))
        self.btn_props.clicked.connect(lambda: self.tabChanged.emit("props"))
