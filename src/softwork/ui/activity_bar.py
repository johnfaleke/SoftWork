"""
Modern IDE Activity Bar for SoftWork CAD.
Provides vertical icon navigation strip to switch views, toggle sidebars, and access tools.
"""
from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional, Dict, Any, List

from softwork.ui.theme import ThemePalette, ThemeManager


class ActivityBar(tk.Frame):
    """
    Vertical activity bar on the far left of the application window.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_tab_changed: Optional[Callable[[str], None]] = None,
        on_settings_clicked: Optional[Callable[[], None]] = None,
        on_ai_clicked: Optional[Callable[[], None]] = None,
        theme: Optional[ThemePalette] = None,
        **kwargs: Any
    ) -> None:
        self.theme = theme or ThemeManager.get_instance().current_theme
        kwargs.setdefault("bg", self.theme.bg_app)
        kwargs.setdefault("width", 48)
        kwargs.setdefault("relief", tk.FLAT)
        super().__init__(parent, **kwargs)

        self.on_tab_changed = on_tab_changed
        self.on_settings_clicked = on_settings_clicked
        self.on_ai_clicked = on_ai_clicked
        self.active_tab: str = "tree"

        self._build_ui()

    def apply_theme(self, theme: ThemePalette) -> None:
        self.theme = theme
        self.configure(bg=theme.bg_app)
        self._build_ui()

    def _build_ui(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        th = self.theme

        # Top Group: Navigation Icons
        top_group = tk.Frame(self, bg=th.bg_app)
        top_group.pack(side=tk.TOP, fill=tk.X, pady=(6, 0))

        tabs = [
            ("tree", "📁", "Model Tree & Features"),
            ("tools", "🛠️", "CAD Modeling Tools"),
            ("props", "📊", "Feature Properties"),
        ]

        self.btn_map: Dict[str, tk.Button] = {}

        for tab_id, icon, tooltip in tabs:
            is_active = (self.active_tab == tab_id)
            btn = tk.Button(
                top_group,
                text=icon,
                bg=th.bg_hover if is_active else th.bg_app,
                fg=th.fg_accent if is_active else th.fg_secondary,
                activebackground=th.bg_hover,
                activeforeground=th.fg_accent,
                font=("Segoe UI", 12),
                bd=0,
                width=3,
                height=1,
                cursor="hand2",
                command=lambda t=tab_id: self._select_tab(t),
            )
            btn.pack(pady=4, padx=4)
            self.btn_map[tab_id] = btn

        # Bottom Group: AI Copilot & Settings
        bottom_group = tk.Frame(self, bg=th.bg_app)
        bottom_group.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))

        btn_ai = tk.Button(
            bottom_group,
            text="✨",
            bg=th.bg_app,
            fg=th.fg_accent,
            activebackground=th.bg_hover,
            activeforeground=th.fg_accent,
            font=("Segoe UI", 12),
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            command=self._on_ai_click,
        )
        btn_ai.pack(pady=4, padx=4)

        btn_settings = tk.Button(
            bottom_group,
            text="⚙️",
            bg=th.bg_app,
            fg=th.fg_secondary,
            activebackground=th.bg_hover,
            activeforeground=th.fg_primary,
            font=("Segoe UI", 12),
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            command=self._on_settings_click,
        )
        btn_settings.pack(pady=4, padx=4)

    def _select_tab(self, tab_id: str) -> None:
        self.active_tab = tab_id
        self._build_ui()
        if self.on_tab_changed:
            self.on_tab_changed(tab_id)

    def _on_ai_click(self) -> None:
        if self.on_ai_clicked:
            self.on_ai_clicked()

    def _on_settings_click(self) -> None:
        if self.on_settings_clicked:
            self.on_settings_clicked()
