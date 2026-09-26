"""
Modern Workspace Settings & Theme Preferences Dialog for SoftWork CAD.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from softwork.ui.theme import ThemeManager, ThemePalette
from softwork.ui.workspace_settings import WorkspaceSettings, WorkspaceSettingsManager


class WorkspaceSettingsDialog(tk.Toplevel):
    """
    Modal preferences window for configuring themes, grid, camera, shading, and units.
    All theme choices (Obsidian Pitch, Monochrome Charcoal, Studio Light, Nordic Frost, etc.) are managed here.
    """

    def __init__(
        self,
        parent: tk.Tk,
        on_settings_applied: Optional[Callable[[WorkspaceSettings, ThemePalette], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.title("Workspace Settings and Theme Preferences — SoftWork")
        self.geometry("580x560")
        self.minsize(520, 500)
        self.transient(parent)
        self.grab_set()

        self.on_settings_applied = on_settings_applied
        self.theme_manager = ThemeManager.get_instance()
        self.settings_manager = WorkspaceSettingsManager.get_instance()
        self.settings = self.settings_manager.settings

        theme = self.theme_manager.current_theme
        self.configure(bg=theme.bg_panel)

        self._build_ui(theme)

    def _build_ui(self, theme: ThemePalette) -> None:
        # Header
        header = tk.Frame(self, bg=theme.bg_card, padx=18, pady=14)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Workspace and Theme Preferences",
            font=("Segoe UI", 12, "bold"),
            bg=theme.bg_card,
            fg=theme.fg_accent,
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Select from 8 crafted theme presets or customize viewport, grid, and engineering units.",
            font=("Segoe UI", 9),
            bg=theme.bg_card,
            fg=theme.fg_secondary,
        ).pack(anchor=tk.W)

        # Tabbed notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        # Tab 1: Appearance & Theme Presets
        tab_theme = tk.Frame(notebook, bg=theme.bg_panel, padx=14, pady=14)
        notebook.add(tab_theme, text="Theme and Styling")

        tk.Label(
            tab_theme,
            text="Color Theme Preset:",
            bg=theme.bg_panel,
            fg=theme.fg_primary,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky=tk.W, pady=8)

        self.theme_var = tk.StringVar(value=self.theme_manager.active_theme_name)
        theme_combo = ttk.Combobox(
            tab_theme,
            textvariable=self.theme_var,
            values=list(self.theme_manager.themes.keys()),
            state="readonly",
            width=32,
            font=("Segoe UI", 9),
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=8, padx=8)

        # Theme Swatch Preview Box
        self.swatch_frame = tk.Frame(tab_theme, bg=theme.bg_card, relief="flat", padx=12, pady=10)
        self.swatch_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=12)

        self.lbl_swatch_title = tk.Label(
            self.swatch_frame,
            text="Theme Preview: True Black and High Contrast Sketches",
            font=("Segoe UI", 9, "bold"),
            bg=theme.bg_card,
            fg=theme.fg_accent,
        )
        self.lbl_swatch_title.pack(anchor=tk.W)

        self.lbl_swatch_desc = tk.Label(
            self.swatch_frame,
            text="Optimized for OLED & Dark workflows with black/grey backgrounds and high-visibility CAD elements.",
            font=("Segoe UI", 8),
            bg=theme.bg_card,
            fg=theme.fg_secondary,
            wraplength=480,
            justify=tk.LEFT,
        )
        self.lbl_swatch_desc.pack(anchor=tk.W, pady=(2, 0))

        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_selected)

        tk.Label(
            tab_theme,
            text="Default Unit System:",
            bg=theme.bg_panel,
            fg=theme.fg_primary,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.unit_var = tk.StringVar(value=self.settings.default_unit)
        unit_combo = ttk.Combobox(
            tab_theme,
            textvariable=self.unit_var,
            values=["mm", "cm", "m", "in"],
            state="readonly",
            width=12,
        )
        unit_combo.grid(row=2, column=1, sticky=tk.W, pady=8, padx=8)

        # Tab 2: 3D Viewport & Grid
        tab_view = tk.Frame(notebook, bg=theme.bg_panel, padx=14, pady=14)
        notebook.add(tab_view, text="3D Viewport and Grid")

        self.grid_var = tk.BooleanVar(value=self.settings.show_grid)
        cb_grid = tk.Checkbutton(
            tab_view,
            text="Show 3D CAD Ground Grid",
            variable=self.grid_var,
            bg=theme.bg_panel,
            fg=theme.fg_primary,
            selectcolor=theme.bg_card,
            activebackground=theme.bg_panel,
            activeforeground=theme.fg_primary,
        )
        cb_grid.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=6)

        tk.Label(tab_view, text="Grid Spacing (mm):", bg=theme.bg_panel, fg=theme.fg_primary).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.grid_step_var = tk.StringVar(value=str(self.settings.grid_step))
        ent_grid_step = tk.Entry(tab_view, textvariable=self.grid_step_var, bg=theme.bg_input, fg=theme.fg_primary, width=10, relief="flat")
        ent_grid_step.grid(row=1, column=1, sticky=tk.W, pady=4, padx=8)

        tk.Label(tab_view, text="Shading Mode:", bg=theme.bg_panel, fg=theme.fg_primary).grid(row=2, column=0, sticky=tk.W, pady=6)
        self.shading_var = tk.StringVar(value=self.settings.shading_mode)
        shading_combo = ttk.Combobox(
            tab_view,
            textvariable=self.shading_var,
            values=["shaded_edges", "shaded", "wireframe"],
            state="readonly",
            width=16,
        )
        shading_combo.grid(row=2, column=1, sticky=tk.W, pady=6, padx=8)

        self.ghost_var = tk.BooleanVar(value=self.settings.show_ghost_preview)
        cb_ghost = tk.Checkbutton(
            tab_view,
            text="Show AI Ghost Mesh Volume Predictions",
            variable=self.ghost_var,
            bg=theme.bg_panel,
            fg=theme.fg_primary,
            selectcolor=theme.bg_card,
            activebackground=theme.bg_panel,
            activeforeground=theme.fg_primary,
        )
        cb_ghost.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=6)

        self.axes_var = tk.BooleanVar(value=self.settings.show_axes)
        cb_axes = tk.Checkbutton(
            tab_view,
            text="Show Coordinate Axes Gizmo (X/Y/Z)",
            variable=self.axes_var,
            bg=theme.bg_panel,
            fg=theme.fg_primary,
            selectcolor=theme.bg_card,
            activebackground=theme.bg_panel,
            activeforeground=theme.fg_primary,
        )
        cb_axes.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=6)

        # Bottom Button Bar
        btn_bar = tk.Frame(self, bg=theme.bg_card, padx=16, pady=12)
        btn_bar.pack(side=tk.BOTTOM, fill=tk.X)

        btn_cancel = ttk.Button(btn_bar, text="Cancel", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=4)

        btn_apply = ttk.Button(btn_bar, text="Apply & Save", style="Accent.TButton", command=self._apply_and_save)
        btn_apply.pack(side=tk.RIGHT, padx=4)

    def _on_theme_selected(self, event: tk.Event) -> None:
        sel_name = self.theme_var.get()
        target = self.theme_manager.themes.get(sel_name)
        if target:
            self.lbl_swatch_title.config(text=f"Theme Preview: {target.name}", fg=target.fg_accent)
            mode_desc = "Dark / OLED high contrast" if target.is_dark else "Clean Light mode"
            self.lbl_swatch_desc.config(text=f"{mode_desc} | Solid: {target.viewport_solid} | Sketch Wire: {target.viewport_sketch_line}")

    def _apply_and_save(self) -> None:
        # Update theme
        selected_theme = self.theme_var.get()
        self.theme_manager.set_theme(selected_theme)
        palette = self.theme_manager.current_theme

        # Update settings
        try:
            grid_step = float(self.grid_step_var.get())
        except ValueError:
            grid_step = 20.0

        self.settings.theme_name = selected_theme
        self.settings.default_unit = self.unit_var.get()
        self.settings.show_grid = self.grid_var.get()
        self.settings.grid_step = max(5.0, min(200.0, grid_step))
        self.settings.shading_mode = self.shading_var.get()
        self.settings.show_ghost_preview = self.ghost_var.get()
        self.settings.show_axes = self.axes_var.get()

        # Save to disk
        self.settings_manager.save_settings(self.settings)

        if self.on_settings_applied:
            self.on_settings_applied(self.settings, palette)

        self.destroy()
        messagebox.showinfo("Settings Applied", f"Active workspace theme updated to: {selected_theme}")
