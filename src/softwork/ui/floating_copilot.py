"""
Modern Floating & Draggable AI Copilot HUD Widget for SoftWork CAD.
Can be moved freely across the 3D canvas, expanded into a full conversational assistant,
or collapsed into a sleek floating action pill.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any, List

from softwork.ai.agent import CADAgent, AgentExecutionResult, AgentPlan
from softwork.ui.theme import ThemePalette, ThemeManager


class FloatingAICopilot(tk.Frame):
    """
    Draggable, collapsible, and expandable floating AI Copilot window inside the 3D Viewport.
    """

    def __init__(
        self,
        parent: tk.Widget,
        agent: CADAgent,
        on_plan_preview: Optional[Callable[[AgentPlan], None]] = None,
        on_prompt_executed: Optional[Callable[[AgentExecutionResult], None]] = None,
        theme: Optional[ThemePalette] = None,
        **kwargs: Any
    ) -> None:
        self.theme = theme or ThemeManager.get_instance().current_theme
        kwargs.setdefault("bg", self.theme.bg_card)
        kwargs.setdefault("highlightbackground", self.theme.border)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("relief", tk.FLAT)
        super().__init__(parent, **kwargs)

        self.agent = agent
        self.on_plan_preview = on_plan_preview
        self.on_prompt_executed = on_prompt_executed

        # State: "COLLAPSED", "EXPANDED"
        self.is_expanded: bool = False
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0

        # Position tracking
        self.pos_x: int = 24
        self.pos_y: int = 48

        self._build_ui()

    def apply_theme(self, theme: ThemePalette) -> None:
        self.theme = theme
        self.configure(bg=theme.bg_card, highlightbackground=theme.border)
        self._build_ui()

    def _build_ui(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        th = self.theme

        # Header Bar (Draggable)
        self.header = tk.Frame(self, bg=th.bg_panel, height=28, cursor="fleur", padx=8, pady=4)
        self.header.pack(fill=tk.X)

        self.lbl_title = tk.Label(
            self.header,
            text="PARAMETRIC COPILOT",
            bg=th.bg_panel,
            fg=th.fg_primary,
            font=("Segoe UI", 9, "bold"),
            cursor="fleur",
        )
        self.lbl_title.pack(side=tk.LEFT, padx=4)

        # Provider pill badge
        prov_name = type(self.agent.provider).__name__.replace("Provider", "")
        lbl_badge = tk.Label(
            self.header,
            text=prov_name.upper(),
            bg=th.bg_hover,
            fg=th.fg_accent,
            font=("Segoe UI", 7, "bold"),
            padx=4,
            pady=1,
        )
        lbl_badge.pack(side=tk.LEFT, padx=4)

        # Toggle Expand/Collapse Button
        btn_toggle_text = "Collapse" if self.is_expanded else "Expand"
        self.btn_toggle = tk.Button(
            self.header,
            text=btn_toggle_text,
            bg=th.bg_panel,
            fg=th.fg_secondary,
            activebackground=th.bg_hover,
            activeforeground=th.fg_primary,
            bd=0,
            padx=4,
            font=("Segoe UI", 8, "bold"),
            command=self.toggle_expanded,
        )
        self.btn_toggle.pack(side=tk.RIGHT)

        # Bind drag events to header and title
        for w in (self.header, self.lbl_title):
            w.bind("<ButtonPress-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_motion)

        if self.is_expanded:
            self._build_expanded_body()
        else:
            self._build_compact_body()

    def _build_compact_body(self) -> None:
        th = self.theme
        body = tk.Frame(self, bg=th.bg_card, padx=8, pady=6)
        body.pack(fill=tk.X)

        input_frame = tk.Frame(body, bg=th.bg_input, highlightbackground=th.border, highlightthickness=1)
        input_frame.pack(fill=tk.X, expand=True)

        self.entry_prompt = tk.Entry(
            input_frame,
            bg=th.bg_input,
            fg=th.fg_primary,
            insertbackground=th.fg_accent,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            bd=0,
        )
        self.entry_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)
        self.entry_prompt.insert(0, "Create sketch on XY plane")
        self.entry_prompt.bind("<Return>", lambda e: self.submit_prompt())

        btn_send = tk.Button(
            input_frame,
            text="Run",
            bg=th.accent_btn_bg,
            fg=th.accent_btn_fg,
            activebackground=th.accent_btn_hover,
            activeforeground=th.accent_btn_fg,
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            command=self.submit_prompt,
        )
        btn_send.pack(side=tk.RIGHT)

    def _build_expanded_body(self) -> None:
        th = self.theme
        body = tk.Frame(self, bg=th.bg_card, padx=10, pady=8, width=360, height=280)
        body.pack(fill=tk.BOTH, expand=True)

        # Chat & Reason Log Container
        log_frame = tk.Frame(body, bg=th.bg_panel, highlightbackground=th.border, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.txt_log = tk.Text(
            log_frame,
            bg=th.bg_panel,
            fg=th.fg_primary,
            font=("Consolas", 8),
            wrap=tk.WORD,
            bd=0,
            padx=6,
            pady=6,
            height=8,
        )
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.txt_log.insert(tk.END, "[SYSTEM] Parametric Copilot Online.\n[INFO] Enter natural language or parameter instructions.\n\n")
        self.txt_log.config(state=tk.DISABLED)

        # Quick Suggestion Chips
        chips_frame = tk.Frame(body, bg=th.bg_card)
        chips_frame.pack(fill=tk.X, pady=(0, 6))

        chips = ["Plate 100x60", "4x M8 Holes", "Shell 2mm", "Extrude 30mm"]
        for chip in chips:
            btn_chip = tk.Button(
                chips_frame,
                text=chip,
                bg=th.bg_hover,
                fg=th.fg_accent,
                activebackground=th.accent_btn_bg,
                activeforeground=th.accent_btn_fg,
                bd=0,
                font=("Segoe UI", 7, "bold"),
                padx=4,
                pady=2,
                command=lambda c=chip: self._use_chip_prompt(c),
            )
            btn_chip.pack(side=tk.LEFT, padx=2)

        # Prompt Input Field
        input_frame = tk.Frame(body, bg=th.bg_input, highlightbackground=th.border, highlightthickness=1)
        input_frame.pack(fill=tk.X)

        self.entry_prompt = tk.Entry(
            input_frame,
            bg=th.bg_input,
            fg=th.fg_primary,
            insertbackground=th.fg_accent,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            bd=0,
        )
        self.entry_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)
        self.entry_prompt.insert(0, "Create a 100 x 60 x 10 mm mounting plate")
        self.entry_prompt.bind("<Return>", lambda e: self.submit_prompt())

        btn_send = tk.Button(
            input_frame,
            text="Execute",
            bg=th.accent_btn_bg,
            fg=th.accent_btn_fg,
            activebackground=th.accent_btn_hover,
            activeforeground=th.accent_btn_fg,
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            command=self.submit_prompt,
        )
        btn_send.pack(side=tk.RIGHT)

    def _use_chip_prompt(self, chip_text: str) -> None:
        clean = f"Create {chip_text}"
        self.entry_prompt.delete(0, tk.END)
        self.entry_prompt.insert(0, clean)
        self.submit_prompt()

    def toggle_expanded(self) -> None:
        self.is_expanded = not self.is_expanded
        self._build_ui()

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self.pos_x = max(10, self.pos_x + dx)
        self.pos_y = max(10, self.pos_y + dy)
        self.place(x=self.pos_x, y=self.pos_y)

    def append_log(self, text: str) -> None:
        if hasattr(self, "txt_log"):
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.insert(tk.END, text + "\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state=tk.DISABLED)

    def submit_prompt(self) -> None:
        prompt = self.entry_prompt.get().strip()
        if not prompt:
            return

        self.append_log(f"Command: {prompt}")

        # Plan & Preview
        plan = self.agent.plan_prompt(prompt)
        if plan.ghost_mesh and self.on_plan_preview:
            self.on_plan_preview(plan)

        # Execute
        result = self.agent.execute_prompt(prompt)
        if result.success:
            self.append_log(f"Success: {result.explanation}")
        else:
            self.append_log(f"Error: {result.error_message}")

        if self.on_prompt_executed:
            self.on_prompt_executed(result)
