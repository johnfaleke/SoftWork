"""
Modern Draggable & Collapsible Floating AI Copilot Widget for SoftWork Qt6 CAD IDE.
"""
from __future__ import annotations
from typing import Optional, Callable

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
        QScrollArea,
    )
    from PySide6.QtGui import QMouseEvent, QFont, QColor
except ImportError:
    pass


class QtFloatingCopilot(QFrame):
    """
    Floating HUD AI Copilot widget that can be dragged freely over the 3D viewport canvas.
    """
    planPreviewRequested = Signal(object)
    promptExecuted = Signal(object)

    def __init__(self, parent: Optional[QWidget], agent: CADAgent) -> None:
        super().__init__(parent)
        self.agent = agent
        self.is_expanded: bool = False
        self._dragging: bool = False
        self._drag_pos = QPoint()

        self.setFixedWidth(340)
        self.setStyleSheet("""
            QFrame#CopilotFrame {
                background-color: #121212;
                border: 1px solid #282828;
                border-radius: 10px;
            }
            QLabel#CopilotHeader {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel#CopilotBadge {
                background-color: #1F1F1F;
                color: #00F0FF;
                border: 1px solid #00F0FF;
                border-radius: 4px;
                padding: 1px 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QTextEdit#CopilotLog {
                background-color: #0A0A0A;
                color: #E2E8F0;
                border: 1px solid #1E1E1E;
                border-radius: 6px;
                font-family: "Consolas", monospace;
                font-size: 11px;
                padding: 6px;
            }
            QPushButton#ChipButton {
                background-color: #1E1E1E;
                color: #00F0FF;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton#ChipButton:hover {
                background-color: #00F0FF;
                color: #000000;
            }
            QLineEdit#PromptInput {
                background-color: #181818;
                color: #FFFFFF;
                border: 1px solid #2E2E2E;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12px;
            }
            QLineEdit#PromptInput:focus {
                border-color: #00F0FF;
            }
            QPushButton#SendButton {
                background-color: #00F0FF;
                color: #000000;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton#SendButton:hover {
                background-color: #33F3FF;
            }
            QPushButton#ToggleBtn {
                background: transparent;
                color: #888888;
                border: none;
                font-size: 11px;
            }
            QPushButton#ToggleBtn:hover {
                color: #FFFFFF;
            }
        """)
        self.setObjectName("CopilotFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        # Clear existing layout
        if self.layout() is not None:
            QWidget().setLayout(self.layout())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 10)
        main_layout.setSpacing(6)

        # Header (Draggable Handle)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        lbl_icon = QLabel("✨")
        lbl_icon.setStyleSheet("font-size: 13px;")
        header_layout.addWidget(lbl_icon)

        lbl_title = QLabel("SoftWork Copilot")
        lbl_title.setObjectName("CopilotHeader")
        header_layout.addWidget(lbl_title)

        prov_name = type(self.agent.provider).__name__.replace("Provider", "")
        lbl_badge = QLabel(prov_name)
        lbl_badge.setObjectName("CopilotBadge")
        header_layout.addWidget(lbl_badge)

        header_layout.addStretch()

        self.btn_toggle = QPushButton("▼" if self.is_expanded else "▲")
        self.btn_toggle.setObjectName("ToggleBtn")
        self.btn_toggle.setFixedSize(20, 20)
        self.btn_toggle.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.btn_toggle)

        main_layout.addLayout(header_layout)

        if self.is_expanded:
            # Multi-line Chat Log
            self.txt_log = QTextEdit()
            self.txt_log.setObjectName("CopilotLog")
            self.txt_log.setReadOnly(True)
            self.txt_log.setFixedHeight(120)
            self.txt_log.append("🤖 AI Copilot Online.\nAsk to create solids, sketches, holes, or shell geometry.")
            main_layout.addWidget(self.txt_log)

            # Suggestion Chips
            chips_layout = QHBoxLayout()
            chips_layout.setSpacing(4)
            for label, prompt in [
                ("➕ Plate", "Create a 100 x 60 x 10 mm mounting plate"),
                ("🔩 M8 Holes", "Add four M8 holes, 10 mm from each corner"),
                ("🐚 Shell", "Add a 2 mm shell"),
            ]:
                chip_btn = QPushButton(label)
                chip_btn.setObjectName("ChipButton")
                chip_btn.clicked.connect(lambda _, p=prompt: self._use_chip(p))
                chips_layout.addWidget(chip_btn)
            chips_layout.addStretch()
            main_layout.addLayout(chips_layout)

        # Input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)

        self.inp_prompt = QLineEdit()
        self.inp_prompt.setObjectName("PromptInput")
        self.inp_prompt.setPlaceholderText("Ask AI to model or modify...")
        self.inp_prompt.returnPressed.connect(self.submit_prompt)
        input_layout.addWidget(self.inp_prompt)

        btn_send = QPushButton("➔")
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
            self.txt_log.append(f"\n> {prompt}")

        # 1. Preview ghost
        plan = self.agent.plan_prompt(prompt)
        if plan.ghost_mesh:
            self.planPreviewRequested.emit(plan)

        # 2. Execute
        result = self.agent.execute_prompt(prompt)
        if hasattr(self, "txt_log") and self.is_expanded:
            if result.success:
                self.txt_log.append(f"✓ {result.explanation}")
            else:
                self.txt_log.append(f"⚠️ {result.error_message}")

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
