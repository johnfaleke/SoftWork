"""
Clean CAD HUD Parametric Copilot Widget for SoftWork (PTC Creo & SolidWorks aesthetic).
"""
from __future__ import annotations
from typing import Optional

from softwork.ai.agent import CADAgent, AgentPlan, AgentExecutionResult

try:
    from PySide6.QtCore import Qt, QPoint, Signal
    from PySide6.QtWidgets import (
        QWidget,
        QFrame,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTextEdit,
    )
    from PySide6.QtGui import QMouseEvent, QFont, QColor
except ImportError:
    pass


class QtFloatingCopilot(QFrame):
    """
    Floating CAD Engineering HUD Copilot widget overlaid on the 3D viewport canvas.
    """
    planPreviewRequested = Signal(object)
    promptExecuted = Signal(object)

    def __init__(self, parent: Optional[QWidget], agent: CADAgent) -> None:
        super().__init__(parent)
        self.agent = agent
        self.is_expanded: bool = False
        self._dragging: bool = False
        self._drag_pos = QPoint()

        self.setFixedWidth(360)
        self.setStyleSheet("""
            QFrame#CopilotFrame {
                background-color: #21252B;
                border: 1px solid #3E4451;
                border-radius: 4px;
            }
            QLabel#CopilotHeader {
                color: #DCE1E8;
                font-family: "Segoe UI", "Tahoma", sans-serif;
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }
            QLabel#CopilotBadge {
                background-color: #1E2227;
                color: #00A8FF;
                border: 1px solid #007ACC;
                border-radius: 2px;
                padding: 1px 5px;
                font-size: 9px;
                font-weight: 600;
            }
            QTextEdit#CopilotLog {
                background-color: #181A1F;
                color: #DCE1E8;
                border: 1px solid #2C313A;
                border-radius: 2px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 10px;
                padding: 4px;
            }
            QPushButton#ChipButton {
                background-color: #282C34;
                color: #DCE1E8;
                border: 1px solid #3E4451;
                border-radius: 2px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: 600;
            }
            QPushButton#ChipButton:hover {
                background-color: #007ACC;
                color: #FFFFFF;
                border-color: #00A8FF;
            }
            QLineEdit#PromptInput {
                background-color: #181A1F;
                color: #DCE1E8;
                border: 1px solid #3E4451;
                border-radius: 2px;
                padding: 5px 6px;
                font-size: 11px;
                font-family: "Segoe UI", "Tahoma", sans-serif;
            }
            QLineEdit#PromptInput:focus {
                border-color: #00A8FF;
            }
            QPushButton#SendButton {
                background-color: #007ACC;
                color: #FFFFFF;
                border: 1px solid #00A8FF;
                border-radius: 2px;
                font-weight: 600;
                font-size: 11px;
                padding: 4px 10px;
            }
            QPushButton#SendButton:hover {
                background-color: #0088DD;
            }
            QPushButton#SendButton:pressed {
                background-color: #0060A0;
            }
            QPushButton#ToggleBtn {
                background: transparent;
                color: #8B949E;
                border: 1px solid #3E4451;
                border-radius: 2px;
                font-size: 9px;
                font-weight: bold;
                padding: 1px;
            }
            QPushButton#ToggleBtn:hover {
                color: #FFFFFF;
                background-color: #282C34;
            }
        """)
        self.setObjectName("CopilotFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        if self.layout() is not None:
            QWidget().setLayout(self.layout())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 8)
        main_layout.setSpacing(5)

        # Header (Draggable Handle)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        lbl_title = QLabel("PARAMETRIC COPILOT")
        lbl_title.setObjectName("CopilotHeader")
        header_layout.addWidget(lbl_title)

        prov_name = type(self.agent.provider).__name__.replace("Provider", "")
        lbl_badge = QLabel(prov_name.upper())
        lbl_badge.setObjectName("CopilotBadge")
        header_layout.addWidget(lbl_badge)

        header_layout.addStretch()

        self.btn_toggle = QPushButton("Collapse" if self.is_expanded else "Expand")
        self.btn_toggle.setObjectName("ToggleBtn")
        self.btn_toggle.setFixedSize(58, 20)
        self.btn_toggle.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.btn_toggle)

        main_layout.addLayout(header_layout)

        if self.is_expanded:
            # Multi-line Command Log
            self.txt_log = QTextEdit()
            self.txt_log.setObjectName("CopilotLog")
            self.txt_log.setReadOnly(True)
            self.txt_log.setFixedHeight(110)
            self.txt_log.append("SYSTEM: Parametric Copilot Online.")
            self.txt_log.append("INFO: Ready for CAD commands, dimension modifications, and feature creation.")
            main_layout.addWidget(self.txt_log)

            # Quick Prompt Chips
            chips_layout = QHBoxLayout()
            chips_layout.setSpacing(4)
            for label, prompt in [
                ("Plate 100x60", "Create a 100 x 60 x 10 mm mounting plate"),
                ("M8 Holes", "Add four M8 holes, 10 mm from each corner"),
                ("2mm Shell", "Add a 2 mm shell"),
            ]:
                chip_btn = QPushButton(label)
                chip_btn.setObjectName("ChipButton")
                chip_btn.clicked.connect(lambda _, p=prompt: self._use_chip(p))
                chips_layout.addWidget(chip_btn)
            chips_layout.addStretch()
            main_layout.addLayout(chips_layout)

        # Input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(4)

        self.inp_prompt = QLineEdit()
        self.inp_prompt.setObjectName("PromptInput")
        self.inp_prompt.setPlaceholderText("Enter CAD instruction or parameter...")
        self.inp_prompt.returnPressed.connect(self.submit_prompt)
        input_layout.addWidget(self.inp_prompt)

        btn_send = QPushButton("Execute")
        btn_send.setObjectName("SendButton")
        btn_send.clicked.connect(self.submit_prompt)
        input_layout.addWidget(btn_send)

        main_layout.addLayout(input_layout)

    def toggle_expanded(self) -> None:
        self.is_expanded = not self.is_expanded
        self._build_ui()
        self.adjustSize()

    def _use_chip(self, prompt: str) -> None:
        self.inp_prompt.setText(prompt)
        self.submit_prompt()

    def submit_prompt(self) -> None:
        prompt = self.inp_prompt.text().strip()
        if not prompt:
            return

        if hasattr(self, "txt_log") and self.is_expanded:
            self.txt_log.append(f"\nCommand: {prompt}")

        # 1. Preview ghost
        plan = self.agent.plan_prompt(prompt)
        if plan.ghost_mesh:
            self.planPreviewRequested.emit(plan)

        # 2. Execute
        result = self.agent.execute_prompt(prompt)
        if hasattr(self, "txt_log") and self.is_expanded:
            if result.success:
                self.txt_log.append(f"Success: {result.explanation}")
            else:
                self.txt_log.append(f"Error: {result.error_message}")

        self.promptExecuted.emit(result)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging = False
