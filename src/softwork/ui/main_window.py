"""
SoftWork Main Window Desktop Interface (IDE Architecture).
Integrates Modern IDE Activity Bar, Draggable Floating AI Copilot HUD, 3D Viewport,
Feature Tree, 2D Sketching, Hole Wizard, Shell, and Workspace Settings.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Tuple

from softwork.ai.agent import CADAgent, AgentExecutionResult, AgentPlan
from softwork.cad.geometry import MeshData
from softwork.commands.feature_commands import (
    CreateBoxCommand,
    CreateMountingPlateCommand,
    CreateSketchCommand,
    ExtrudeSketchCommand,
    RevolveSketchCommand,
    AddHoleWizardCommand,
    AddShellCommand,
    AddPatternCommand,
    AddChamferCommand,
    AddFilletCommand,
)
from softwork.commands.parameter_commands import SetParameterCommand
from softwork.core.document import Document
from softwork.core.feature import Feature, SketchFeature, ExtrudeFeature, RevolveFeature, PatternFeature, ChamferFeature, HoleWizardFeature, ShellFeature
from softwork.document.serializer import save_document, load_document
from softwork.sketch.plane import StandardPlane
from softwork.ui.theme import ThemeManager, ThemePalette, DARK_THEME
from softwork.ui.workspace_settings import WorkspaceSettingsManager, WorkspaceSettings
from softwork.ui.workspace_dialog import WorkspaceSettingsDialog
from softwork.ui.viewport import CAD3DCanvas
from softwork.ui.activity_bar import ActivityBar
from softwork.ui.floating_copilot import FloatingAICopilot


class MainWindow(tk.Tk):
    """
    Primary desktop application window for SoftWork CAD featuring a modern IDE layout.
    """

    def __init__(self, document: Optional[Document] = None) -> None:
        super().__init__()
        self.title("SoftWork CAD — Parametric 3D IDE")
        self.geometry("1360x860")
        self.minsize(1020, 640)

        # Settings and Theme Managers
        self.settings_manager = WorkspaceSettingsManager.get_instance()
        self.theme_manager = ThemeManager.get_instance()
        
        # Load theme from persisted settings
        saved_theme = self.settings_manager.settings.theme_name
        if saved_theme in self.theme_manager.themes:
            self.theme_manager.active_theme_name = saved_theme
        self.theme: ThemePalette = self.theme_manager.current_theme

        self.configure(bg=self.theme.bg_app)

        # Core CAD Document & AI Agent
        self.document: Document = document or Document(name="Untitled.softwork")
        self.agent: CADAgent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)
        self.theme_manager.add_listener(self._on_theme_changed)

        # Build Modern IDE UI layout
        self._setup_styles()
        self._build_menu()
        self._build_ribbon_toolbar()
        self._build_ide_workspace()
        self._build_status_bar()

        # Initial CAD solid generation proof
        if not self.document.active_part.features:
            CreateMountingPlateCommand(
                length=100.0,
                width=60.0,
                thickness=10.0,
                hole_diameter=8.0,
                hole_offset=10.0,
                fillet_radius=2.0,
            ).execute(self.document)

        self._refresh_all()

    def _setup_styles(self) -> None:
        th = self.theme
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=th.bg_app, foreground=th.fg_primary, font=("Segoe UI", 9))
        style.configure("TFrame", background=th.bg_panel)
        style.configure("TLabelframe", background=th.bg_panel, foreground=th.fg_secondary, relief="flat")
        style.configure("TLabelframe.Label", background=th.bg_panel, foreground=th.fg_accent, font=("Segoe UI", 9, "bold"))
        
        style.configure(
            "Treeview",
            background=th.bg_panel,
            foreground=th.fg_primary,
            fieldbackground=th.bg_panel,
            rowheight=26,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", th.accent_btn_bg)], foreground=[("selected", th.accent_btn_fg)])
        
        style.configure("TEntry", fieldbackground=th.bg_input, foreground=th.fg_primary, insertcolor=th.fg_accent)
        style.configure("TButton", background=th.bg_card, foreground=th.fg_primary, relief="flat", padding=[6, 4], font=("Segoe UI", 9))
        style.map("TButton", background=[("active", th.bg_hover), ("pressed", th.accent_btn_hover)])
        
        style.configure("Accent.TButton", background=th.accent_btn_bg, foreground=th.accent_btn_fg, font=("Segoe UI", 9, "bold"), padding=[8, 4])
        style.map("Accent.TButton", background=[("active", th.accent_btn_hover)])

        style.configure("TNotebook", background=th.bg_panel, borderwidth=0)
        style.configure("TNotebook.Tab", background=th.bg_card, foreground=th.fg_primary, padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", th.accent_btn_bg)], foreground=[("selected", th.accent_btn_fg)])

    def _build_menu(self) -> None:
        th = self.theme
        menubar = tk.Menu(self, bg=th.bg_panel, fg=th.fg_primary, activebackground=th.accent_btn_bg, activeforeground=th.accent_btn_fg)

        file_menu = tk.Menu(menubar, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        file_menu.add_command(label="New Part", command=self._action_new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Open .softwork...", command=self._action_open_document, accelerator="Ctrl+O")
        file_menu.add_command(label="Save...", command=self._action_save_document, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export STEP (AP214)...", command=self._action_export_step)
        file_menu.add_command(label="Export STL (Binary)...", command=self._action_export_stl)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        edit_menu.add_command(label="Undo", command=self._action_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._action_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Workspace Settings and Themes...", command=self._action_open_settings)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        design_menu = tk.Menu(menubar, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        design_menu.add_command(label="Create 2D Sketch (XY)", command=lambda: self._action_create_sketch("XY"))
        design_menu.add_command(label="Extrude Active Sketch", command=self._action_extrude_sketch)
        design_menu.add_command(label="Revolve Active Sketch", command=self._action_revolve_sketch)
        design_menu.add_command(label="Add Hole Wizard (ISO Metric)", command=self._action_add_hole_wizard)
        design_menu.add_command(label="Add Shell (Hollow)", command=self._action_add_shell)
        design_menu.add_command(label="Linear Pattern", command=self._action_add_pattern)
        design_menu.add_command(label="Add Chamfer", command=self._action_add_chamfer)
        menubar.add_cascade(label="Design", menu=design_menu)

        view_menu = tk.Menu(menubar, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        view_menu.add_command(label="Isometric View", command=lambda: self.viewport.set_view_isometric())
        view_menu.add_command(label="Top View", command=lambda: self.viewport.set_view_top())
        view_menu.add_command(label="Front View", command=lambda: self.viewport.set_view_front())
        view_menu.add_command(label="Right View", command=lambda: self.viewport.set_view_right())
        view_menu.add_separator()
        view_menu.add_command(label="Reset Camera", command=lambda: self.viewport.reset_view())
        view_menu.add_separator()
        
        # Theme Submenu listing all 8 themes directly
        theme_menu = tk.Menu(view_menu, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        for tname in self.theme_manager.themes.keys():
            theme_menu.add_command(label=tname, command=lambda name=tname: self._switch_theme(name))
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        menubar.add_cascade(label="View", menu=view_menu)

        ai_menu = tk.Menu(menubar, tearoff=0, bg=th.bg_panel, fg=th.fg_primary)
        ai_menu.add_command(label="Toggle Floating AI Copilot", command=self._toggle_ai_copilot)
        ai_menu.add_command(label="Configure Cloud AI Keys (Gemini / Claude / OpenAI)...", command=self._action_configure_api_keys)
        ai_menu.add_separator()
        ai_menu.add_command(label="Run Mounting Plate Flow", command=self._action_run_demo_flow)
        ai_menu.add_command(label="Run Sketch and Extrude Flow", command=self._action_run_sketch_demo)
        menubar.add_cascade(label="AI", menu=ai_menu)

        self.config(menu=menubar)
        self.menubar = menubar

    def _build_ribbon_toolbar(self) -> None:
        th = self.theme
        self.toolbar = tk.Frame(self, bg=th.bg_panel, height=42, padx=8, pady=4, highlightbackground=th.border, highlightthickness=1)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Modeling tools group
        btn_sk = ttk.Button(self.toolbar, text="Sketch", command=lambda: self._action_create_sketch("XY"))
        btn_sk.pack(side=tk.LEFT, padx=2)

        btn_mode_sel = ttk.Button(self.toolbar, text="Select", command=lambda: self._set_draw_mode("SELECT"))
        btn_mode_sel.pack(side=tk.LEFT, padx=2)

        btn_draw_rect = ttk.Button(self.toolbar, text="Rectangle", command=lambda: self._set_draw_mode("DRAW_RECTANGLE"))
        btn_draw_rect.pack(side=tk.LEFT, padx=2)

        btn_draw_circ = ttk.Button(self.toolbar, text="Circle", command=lambda: self._set_draw_mode("DRAW_CIRCLE"))
        btn_draw_circ.pack(side=tk.LEFT, padx=2)

        btn_draw_line = ttk.Button(self.toolbar, text="Line", command=lambda: self._set_draw_mode("DRAW_LINE"))
        btn_draw_line.pack(side=tk.LEFT, padx=2)

        # Separator
        sep1 = tk.Frame(self.toolbar, bg=th.border, width=1, height=24)
        sep1.pack(side=tk.LEFT, padx=6, fill=tk.Y)

        btn_ext = ttk.Button(self.toolbar, text="Extrude", command=self._action_extrude_sketch)
        btn_ext.pack(side=tk.LEFT, padx=2)

        btn_rev = ttk.Button(self.toolbar, text="Revolve", command=self._action_revolve_sketch)
        btn_rev.pack(side=tk.LEFT, padx=2)

        btn_hole = ttk.Button(self.toolbar, text="Hole Wizard", command=self._action_add_hole_wizard)
        btn_hole.pack(side=tk.LEFT, padx=2)

        btn_shell = ttk.Button(self.toolbar, text="Shell", command=self._action_add_shell)
        btn_shell.pack(side=tk.LEFT, padx=2)

        btn_box = ttk.Button(self.toolbar, text="Box Primitive", command=self._action_create_box)
        btn_box.pack(side=tk.LEFT, padx=2)

        btn_plate = ttk.Button(self.toolbar, text="Plate Primitive", command=self._action_create_plate)
        btn_plate.pack(side=tk.LEFT, padx=2)

        # Right tools
        btn_copilot_toggle = tk.Button(
            self.toolbar,
            text="Parametric Copilot",
            bg=th.bg_hover,
            fg=th.fg_accent,
            activebackground=th.accent_btn_bg,
            activeforeground=th.accent_btn_fg,
            bd=0,
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3,
            command=self._toggle_ai_copilot,
        )
        btn_copilot_toggle.pack(side=tk.RIGHT, padx=4)

        btn_settings = ttk.Button(self.toolbar, text="Settings", command=self._action_open_settings)
        btn_settings.pack(side=tk.RIGHT, padx=3)

        btn_redo = ttk.Button(self.toolbar, text="Redo", command=self._action_redo)
        btn_redo.pack(side=tk.RIGHT, padx=2)

        btn_undo = ttk.Button(self.toolbar, text="Undo", command=self._action_undo)
        btn_undo.pack(side=tk.RIGHT, padx=2)

    def _build_ide_workspace(self) -> None:
        th = self.theme
        
        # Workspace container
        self.workspace_frame = tk.Frame(self, bg=th.bg_app)
        self.workspace_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 1. Left Vertical Activity Bar
        self.activity_bar = ActivityBar(
            self.workspace_frame,
            on_tab_changed=self._on_activity_tab_changed,
            on_settings_clicked=self._action_open_settings,
            on_ai_clicked=self._toggle_ai_copilot,
            theme=th,
        )
        self.activity_bar.pack(side=tk.LEFT, fill=tk.Y)

        # 2. Main Horizontal Split Panes
        self.main_pane = tk.PanedWindow(self.workspace_frame, orient=tk.HORIZONTAL, bg=th.bg_app, sashrelief=tk.FLAT, sashwidth=3)
        self.main_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Left Sidebar (Model Tree & Tools)
        self.left_sidebar = tk.Frame(self.main_pane, bg=th.bg_panel, width=280)
        self.main_pane.add(self.left_sidebar, width=280)

        # Sidebar Header
        self.sidebar_header = tk.Frame(self.left_sidebar, bg=th.bg_card, height=28, padx=8, pady=4)
        self.sidebar_header.pack(fill=tk.X)
        self.lbl_sidebar_title = tk.Label(self.sidebar_header, text="MODEL TREE", font=("Segoe UI", 9, "bold"), bg=th.bg_card, fg=th.fg_accent)
        self.lbl_sidebar_title.pack(side=tk.LEFT)

        self.tree_container = tk.Frame(self.left_sidebar, bg=th.bg_panel, padx=4, pady=4)
        self.tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_container, columns=("Type", "Status"), show="tree headings")
        self.tree.heading("#0", text="Feature")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Status", text="Status")
        self.tree.column("#0", width=140)
        self.tree.column("Type", width=70)
        self.tree.column("Status", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Center Viewport Area with Floating AI Copilot Widget
        self.center_viewport_container = tk.Frame(self.main_pane, bg=th.viewport_bg)
        self.main_pane.add(self.center_viewport_container, width=740)

        # Breadcrumb Bar
        self.breadcrumb_bar = tk.Frame(self.center_viewport_container, bg=th.bg_panel, height=24, padx=8, pady=2)
        self.breadcrumb_bar.pack(fill=tk.X)
        self.lbl_breadcrumb = tk.Label(
            self.breadcrumb_bar,
            text="Workspace > Part 1 > Active Solid",
            bg=th.bg_panel,
            fg=th.fg_secondary,
            font=("Segoe UI", 8),
        )
        self.lbl_breadcrumb.pack(side=tk.LEFT)

        # 3D Viewport Canvas
        self.viewport = CAD3DCanvas(
            self.center_viewport_container,
            on_face_selected=self._on_face_picked,
            on_shape_drawn=self._on_viewport_shape_drawn,
            theme=self.theme,
            settings=self.settings_manager.settings,
        )
        self.viewport.pack(fill=tk.BOTH, expand=True)

        # Hovering / Draggable Floating AI Copilot placed directly over the 3D canvas
        self.floating_copilot = FloatingAICopilot(
            self.viewport,
            agent=self.agent,
            on_plan_preview=self._on_copilot_plan_preview,
            on_prompt_executed=self._on_copilot_prompt_executed,
            theme=self.theme,
        )
        self.floating_copilot.place(x=24, y=48)

        # Right Sidebar: Properties Inspector
        self.right_sidebar = tk.Frame(self.main_pane, bg=th.bg_panel, width=300)
        self.main_pane.add(self.right_sidebar, width=300)

        self.prop_header = tk.Frame(self.right_sidebar, bg=th.bg_card, height=28, padx=8, pady=4)
        self.prop_header.pack(fill=tk.X)
        tk.Label(self.prop_header, text="PROPERTIES", font=("Segoe UI", 9, "bold"), bg=th.bg_card, fg=th.fg_accent).pack(side=tk.LEFT)

        self.props_container = tk.Frame(self.right_sidebar, bg=th.bg_panel, padx=8, pady=8)
        self.props_container.pack(fill=tk.BOTH, expand=True)

    def _build_status_bar(self) -> None:
        th = self.theme
        self.status_bar = tk.Label(
            self,
            text="Ready | SoftWork CAD Kernel Active",
            bg=th.bg_panel,
            fg=th.fg_secondary,
            anchor=tk.W,
            padx=12,
            pady=4,
            font=("Segoe UI", 8),
            highlightbackground=th.border,
            highlightthickness=1,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_activity_tab_changed(self, tab_id: str) -> None:
        if tab_id == "tree":
            self.lbl_sidebar_title.config(text="MODEL TREE")
        elif tab_id == "tools":
            self.lbl_sidebar_title.config(text="CAD TOOLS & PRIMITIVES")
        elif tab_id == "props":
            self.lbl_sidebar_title.config(text="INSPECTOR")

    def _toggle_ai_copilot(self) -> None:
        if self.floating_copilot.winfo_ismapped():
            self.floating_copilot.place_forget()
        else:
            self.floating_copilot.place(x=self.floating_copilot.pos_x, y=self.floating_copilot.pos_y)

    def _on_copilot_plan_preview(self, plan: AgentPlan) -> None:
        if plan.ghost_mesh:
            self.viewport.set_ghost_mesh(plan.ghost_mesh, delta_vol=plan.predicted_delta_vol)

    def _on_copilot_prompt_executed(self, result: AgentExecutionResult) -> None:
        if result.success:
            self.status_bar.config(text=f"AI: {result.explanation}", fg=self.theme.fg_accent)
        else:
            self.status_bar.config(text=f"AI Error: {result.error_message}", fg=self.theme.color_error)
            messagebox.showwarning("CAD Agent Notice", result.error_message)
        self._refresh_all()

    def _switch_theme(self, theme_name: str) -> None:
        self.theme_manager.set_theme(theme_name)
        self.settings_manager.settings.theme_name = theme_name
        self.settings_manager.save_settings()

    def _on_theme_changed(self, new_theme: ThemePalette) -> None:
        self.theme = new_theme
        self.configure(bg=new_theme.bg_app)
        self._setup_styles()

        # Update container backgrounds
        self.toolbar.configure(bg=new_theme.bg_panel, highlightbackground=new_theme.border)
        self.workspace_frame.configure(bg=new_theme.bg_app)
        self.main_pane.configure(bg=new_theme.bg_app)
        self.left_sidebar.configure(bg=new_theme.bg_panel)
        self.sidebar_header.configure(bg=new_theme.bg_card)
        self.lbl_sidebar_title.configure(bg=new_theme.bg_card, fg=new_theme.fg_accent)
        self.tree_container.configure(bg=new_theme.bg_panel)
        self.center_viewport_container.configure(bg=new_theme.viewport_bg)
        self.breadcrumb_bar.configure(bg=new_theme.bg_panel)
        self.lbl_breadcrumb.configure(bg=new_theme.bg_panel, fg=new_theme.fg_secondary)
        self.right_sidebar.configure(bg=new_theme.bg_panel)
        self.prop_header.configure(bg=new_theme.bg_card)
        self.props_container.configure(bg=new_theme.bg_panel)
        self.status_bar.configure(bg=new_theme.bg_panel, fg=new_theme.fg_secondary, highlightbackground=new_theme.border)

        # Update sub-widgets
        self.activity_bar.apply_theme(new_theme)
        self.viewport.apply_theme(new_theme)
        self.floating_copilot.apply_theme(new_theme)
        self._build_menu()
        self._refresh_all()

    def _action_open_settings(self) -> None:
        WorkspaceSettingsDialog(
            self,
            on_settings_applied=lambda settings, palette: self.viewport.apply_settings(settings),
        )

    def _set_draw_mode(self, mode: str) -> None:
        active_plane = None
        for f in reversed(self.document.active_part.features):
            if isinstance(f, SketchFeature):
                active_plane = f.sketch.plane
                break
        self.viewport.set_tool_mode(mode, active_plane=active_plane)
        mode_label = mode.replace("DRAW_", "").title() if mode != "SELECT" else "Select / Orbit"
        self.status_bar.config(text=f"Tool Mode: {mode_label} | Click & Drag on 3D Viewport to sketch", fg=self.theme.fg_accent)

    def _on_viewport_shape_drawn(self, shape_type: str, data: Dict[str, Any]) -> None:
        sk_feat = None
        for f in reversed(self.document.active_part.features):
            if isinstance(f, SketchFeature):
                sk_feat = f
                break
        if not sk_feat:
            self._action_create_sketch("XY")
            sk_feat = self.document.active_part.features[-1]

        if isinstance(sk_feat, SketchFeature):
            if shape_type == "rectangle":
                sk_feat.sketch.add_rectangle(
                    width=data["width"],
                    height=data["height"],
                    center_u=data.get("center_u", 0.0),
                    center_v=data.get("center_v", 0.0),
                    centered=data.get("centered", True),
                )
            elif shape_type == "circle":
                sk_feat.sketch.add_circle(
                    radius=data["radius"],
                    center_u=data.get("center_u", 0.0),
                    center_v=data.get("center_v", 0.0),
                )
            elif shape_type == "line":
                sk_feat.sketch.add_line(
                    start_u=data["start_u"],
                    start_v=data["start_v"],
                    end_u=data["end_u"],
                    end_v=data["end_v"],
                )

            self.document.recompute()
            self._refresh_all()
            self.status_bar.config(text=f"Added {shape_type.title()} to {sk_feat.name}", fg=self.theme.color_success)

    def _on_face_picked(self, face_idx: int, normal: Tuple[float, float, float]) -> None:
        self.status_bar.config(
            text=f"Selected Surface: Face #{face_idx} | Normal: ({normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f})",
            fg=self.theme.color_warning,
        )

    def _on_document_changed(self) -> None:
        self._refresh_all()

    def _refresh_all(self) -> None:
        solid = self.document.active_part.active_solid
        mesh = self.document.backend.to_mesh(solid) if solid else None
        self.viewport.set_mesh(mesh)

        sketches = [
            f.sketch for f in self.document.active_part.features
            if isinstance(f, SketchFeature) and getattr(f, "sketch", None) is not None
        ]
        self.viewport.set_sketches(sketches)

        self.tree.delete(*self.tree.get_children())
        part_node = self.tree.insert("", tk.END, text=self.document.active_part.name, open=True)
        for feat in self.document.active_part.features:
            self.tree.insert(
                part_node,
                tk.END,
                iid=feat.id,
                text=feat.name,
                values=(feat.feature_type.value, feat.status.value),
            )

        self._refresh_properties()

        # Update breadcrumb
        feat_name = self.document.active_part.features[-1].name if self.document.active_part.features else "Empty"
        self.lbl_breadcrumb.config(text=f"{self.document.name} / {self.document.active_part.name} / {feat_name}")

        val = self.document.latest_validation
        if val and not val.is_valid:
            self.status_bar.config(text=f"Validation Issue: {val.issues[0].message}", fg=self.theme.color_error)
        else:
            vol = solid.volume if solid else 0.0
            num_sk = len(sketches)
            sk_info = f" | {num_sk} Sketch(es) active" if num_sk > 0 else ""
            self.status_bar.config(text=f"Solid Valid | Volume: {vol:,.1f} mm3{sk_info} | Theme: {self.theme.name}", fg=self.theme.color_success)

    def _refresh_properties(self) -> None:
        for widget in self.props_container.winfo_children():
            widget.destroy()

        feat_id = self.document.selection.primary_feature_id
        if not feat_id and self.document.active_part.features:
            feat_id = self.document.active_part.features[-1].id

        feature = self.document.get_feature(feat_id) if feat_id else None
        th = self.theme
        if not feature:
            lbl = tk.Label(self.props_container, text="No feature selected", bg=th.bg_panel, fg=th.fg_muted)
            lbl.pack(pady=20)
            return

        tk.Label(self.props_container, text=f"Feature: {feature.name}", bg=th.bg_panel, fg=th.fg_accent, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        tk.Label(self.props_container, text=f"Type: {feature.feature_type.value.upper()}", bg=th.bg_panel, fg=th.fg_secondary).pack(anchor=tk.W)

        # Show sketch profile details if SketchFeature
        if isinstance(feature, SketchFeature):
            tk.Label(self.props_container, text=f"Plane: {feature.sketch.plane.plane_type.value}", bg=th.bg_panel, fg=th.fg_primary).pack(anchor=tk.W, pady=4)
            num_prof = len(feature.sketch.profiles)
            num_el = len(feature.sketch.elements)
            num_c = len(feature.sketch.constraints)
            tk.Label(self.props_container, text=f"Elements: {num_el} | Loops: {num_prof} | Constraints: {num_c}", bg=th.bg_panel, fg=th.color_success).pack(anchor=tk.W, pady=2)
            
            btn_frame = tk.Frame(self.props_container, bg=th.bg_panel)
            btn_frame.pack(fill=tk.X, pady=6)
            btn_add_rect = ttk.Button(btn_frame, text="Add 50x30 Rectangle", command=lambda: self._add_rect_to_sketch(feature, 50.0, 30.0))
            btn_add_rect.pack(fill=tk.X, pady=2)
            btn_add_circ = ttk.Button(btn_frame, text="Add R15 Circle", command=lambda: self._add_circ_to_sketch(feature, 15.0))
            btn_add_circ.pack(fill=tk.X, pady=2)

            btn_solve = ttk.Button(btn_frame, text="Solve Constraints", command=lambda: self._solve_sketch_constraints(feature))
            btn_solve.pack(fill=tk.X, pady=2)

            btn_ext = ttk.Button(btn_frame, text="Extrude This Sketch", style="Accent.TButton", command=self._action_extrude_sketch)
            btn_ext.pack(fill=tk.X, pady=4)
            return

        for param_name, param in feature.parameters.items():
            row = tk.Frame(self.props_container, bg=th.bg_panel)
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=f"{param_name.capitalize()}:", bg=th.bg_panel, fg=th.fg_primary, width=14, anchor=tk.W).pack(side=tk.LEFT)

            entry = tk.Entry(row, bg=th.bg_input, fg=th.fg_primary, insertbackground=th.fg_accent, width=10, relief="flat")
            entry.insert(0, str(param.value))
            entry.pack(side=tk.LEFT, padx=4)

            tk.Label(row, text=param.unit, bg=th.bg_panel, fg=th.fg_secondary).pack(side=tk.LEFT)

            def make_handler(f_id: str, p_name: str, ent: tk.Entry):
                return lambda: self._apply_param_edit(f_id, p_name, ent.get())

            btn = ttk.Button(row, text="Apply", width=6, command=make_handler(feature.id, param_name, entry))
            btn.pack(side=tk.RIGHT, padx=2)

    def _solve_sketch_constraints(self, sk_feat: SketchFeature) -> None:
        report = sk_feat.sketch.solve()
        self.document.recompute()
        self._refresh_all()
        status_msg = f"Solver Converged ({report.iterations} iters) | DOF: {report.degrees_of_freedom}" if report.is_converged else f"Unresolved: {', '.join(report.unresolved_constraints)}"
        messagebox.showinfo("2D Constraint Solver Report", status_msg)

    def _add_rect_to_sketch(self, sk_feat: SketchFeature, w: float = 50.0, h: float = 30.0) -> None:
        sk_feat.sketch.add_rectangle(w, h, centered=True)
        self.document.recompute()
        self._refresh_all()

    def _add_circ_to_sketch(self, sk_feat: SketchFeature, r: float = 15.0) -> None:
        sk_feat.sketch.add_circle(r)
        self.document.recompute()
        self._refresh_all()

    def _apply_param_edit(self, feature_id: str, parameter_name: str, val_str: str) -> None:
        try:
            new_val = float(val_str)
            SetParameterCommand(feature_id, parameter_name, new_val).execute(self.document)
        except ValueError:
            messagebox.showerror("Invalid Input", f"Could not parse numeric value '{val_str}'")

    def _on_tree_select(self, event: tk.Event) -> None:
        selected = self.tree.selection()
        if selected:
            feat_id = selected[0]
            self.document.selection.select_feature(feat_id)
            self._refresh_properties()

    def _action_configure_api_keys(self) -> None:
        from softwork.ai.provider import HeuristicEngineProvider, GeminiProvider, OpenAIProvider, AnthropicProvider
        dlg = tk.Toplevel(self)
        dlg.title("Configure AI Cloud Providers")
        dlg.geometry("460x280")
        dlg.configure(bg=self.theme.bg_panel)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="SoftWork AI Cloud Provider Setup", font=("Segoe UI", 11, "bold"), bg=self.theme.bg_panel, fg=self.theme.fg_accent).pack(pady=10)
        
        frame = tk.Frame(dlg, bg=self.theme.bg_panel, padx=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Active Provider:", bg=self.theme.bg_panel, fg=self.theme.fg_primary).grid(row=0, column=0, sticky=tk.W, pady=6)
        prov_var = tk.StringVar(value="Offline Heuristic Engine")
        combo = ttk.Combobox(frame, textvariable=prov_var, values=["Offline Heuristic Engine", "Google Gemini (1.5 Pro)", "OpenAI (GPT-4o)", "Anthropic (Claude 3.5)"], state="readonly", width=26)
        combo.grid(row=0, column=1, pady=6)

        tk.Label(frame, text="API Key:", bg=self.theme.bg_panel, fg=self.theme.fg_primary).grid(row=1, column=0, sticky=tk.W, pady=6)
        key_entry = tk.Entry(frame, bg=self.theme.bg_input, fg=self.theme.fg_primary, insertbackground=self.theme.fg_accent, width=28, show="*")
        key_entry.grid(row=1, column=1, pady=6)

        def apply_provider():
            chosen = prov_var.get()
            key = key_entry.get().strip()
            if "Gemini" in chosen:
                self.agent.set_provider(GeminiProvider(api_key=key))
            elif "OpenAI" in chosen:
                self.agent.set_provider(OpenAIProvider(api_key=key))
            elif "Anthropic" in chosen:
                self.agent.set_provider(AnthropicProvider(api_key=key))
            else:
                self.agent.set_provider(HeuristicEngineProvider())
            dlg.destroy()
            messagebox.showinfo("AI Configured", f"Active AI Provider updated to: {chosen}")

        btn_save = ttk.Button(dlg, text="Save & Activate", style="Accent.TButton", command=apply_provider)
        btn_save.pack(pady=12)

    def _action_add_hole_wizard(self) -> None:
        if not self.document.active_part.features:
            self._action_create_plate()
        target_feat = self.document.active_part.features[0]
        AddHoleWizardCommand(target_feature_id=target_feat.id, metric_size="M8", hole_type="counterbore", depth=25.0).execute(self.document)
        self._refresh_all()

    def _action_add_shell(self) -> None:
        if not self.document.active_part.features:
            self._action_create_box()
        target_feat = self.document.active_part.features[0]
        AddShellCommand(target_feature_id=target_feat.id, wall_thickness=2.0).execute(self.document)
        self._refresh_all()

    def _action_create_sketch(self, plane: str = "XY") -> None:
        CreateSketchCommand(name=f"Sketch_{plane}", plane_type=StandardPlane(plane)).execute(self.document)
        sk_feat = self.document.active_part.features[-1]
        if isinstance(sk_feat, SketchFeature):
            sk_feat.sketch.add_rectangle(60.0, 40.0, centered=True)
            self.document.selection.select_feature(sk_feat.id)
            self.document.recompute()
            self._refresh_all()

    def _action_extrude_sketch(self) -> None:
        sk_feat = None
        sel_id = self.document.selection.primary_feature_id
        if sel_id:
            f = self.document.get_feature(sel_id)
            if isinstance(f, SketchFeature):
                sk_feat = f

        if not sk_feat:
            for f in reversed(self.document.active_part.features):
                if isinstance(f, SketchFeature):
                    sk_feat = f
                    break

        if not sk_feat:
            self._action_create_sketch("XY")
            sk_feat = self.document.active_part.features[-1]

        if isinstance(sk_feat, SketchFeature):
            if not sk_feat.sketch.elements:
                sk_feat.sketch.add_rectangle(50.0, 30.0, centered=True)
                self.document.recompute()
            ExtrudeSketchCommand(sketch_feature_id=sk_feat.id, distance=25.0).execute(self.document)
            self._refresh_all()

    def _action_revolve_sketch(self) -> None:
        sk_feat = None
        sel_id = self.document.selection.primary_feature_id
        if sel_id:
            f = self.document.get_feature(sel_id)
            if isinstance(f, SketchFeature):
                sk_feat = f

        if not sk_feat:
            for f in reversed(self.document.active_part.features):
                if isinstance(f, SketchFeature):
                    sk_feat = f
                    break

        if not sk_feat:
            CreateSketchCommand(name="Sketch_XY", plane_type=StandardPlane.XY).execute(self.document)
            sk_feat = self.document.active_part.features[-1]
            if isinstance(sk_feat, SketchFeature):
                sk_feat.sketch.add_rectangle(30.0, 50.0, center_u=25.0, center_v=0.0)

        RevolveSketchCommand(sketch_feature_id=sk_feat.id, angle_deg=360.0).execute(self.document)
        self._refresh_all()

    def _action_add_pattern(self) -> None:
        if self.document.active_part.features:
            feat = self.document.active_part.features[-1]
            AddPatternCommand(target_feature_id=feat.id, count_x=3, count_y=1, spacing_x=30.0).execute(self.document)

    def _action_add_chamfer(self) -> None:
        if self.document.active_part.features:
            feat = self.document.active_part.features[0]
            AddChamferCommand(target_feature_id=feat.id, distance=1.5).execute(self.document)

    def _action_run_sketch_demo(self) -> None:
        self.document = Document(name="SketchExtrudeDemo.softwork")
        self.agent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)

        self.agent.execute_prompt("Create sketch on XY plane")
        self.agent.execute_prompt("Add a 100 x 60 mm rectangle to sketch")
        self.agent.execute_prompt("Extrude the sketch by 25 mm")
        self._refresh_all()
        messagebox.showinfo("Sketch Demo", "Successfully created 2D Sketch and extruded into 3D Solid!")

    def _action_run_demo_flow(self) -> None:
        self.agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.agent.execute_prompt("Add four M8 holes, 10 mm from each corner")
        self.agent.execute_prompt("Fillet the outer edges by 2 mm")
        self.agent.execute_prompt("Make it 15 mm thick")
        messagebox.showinfo("Demo Completed", "SoftWork MVP Flow successfully executed!")

    def _action_create_box(self) -> None:
        CreateBoxCommand(width=100.0, height=60.0, depth=10.0).execute(self.document)

    def _action_create_plate(self) -> None:
        CreateMountingPlateCommand(length=100.0, width=60.0, thickness=10.0, hole_diameter=8.0, hole_offset=10.0, fillet_radius=2.0).execute(self.document)

    def _action_undo(self) -> None:
        if self.document.history.can_undo:
            self.document.history.undo()
            self.document.recompute()

    def _action_redo(self) -> None:
        if self.document.history.can_redo:
            self.document.history.redo()
            self.document.recompute()

    def _action_export_step(self) -> None:
        solid = self.document.active_part.active_solid
        if not solid:
            messagebox.showwarning("Export Warning", "No active solid geometry to export.")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".step", filetypes=[("STEP Files", "*.step *.stp")])
        if fp:
            self.document.backend.export_step(solid, fp)
            messagebox.showinfo("Export Successful", f"STEP model exported to:\n{fp}")

    def _action_export_stl(self) -> None:
        solid = self.document.active_part.active_solid
        if not solid:
            messagebox.showwarning("Export Warning", "No active solid geometry to export.")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".stl", filetypes=[("STL Files", "*.stl")])
        if fp:
            self.document.backend.export_stl(solid, fp, binary=True)
            messagebox.showinfo("Export Successful", f"Binary STL mesh exported to:\n{fp}")

    def _action_save_document(self) -> None:
        fp = filedialog.asksaveasfilename(defaultextension=".softwork", filetypes=[("SoftWork Documents", "*.softwork")])
        if fp:
            save_document(self.document, fp)
            messagebox.showinfo("Saved", f"Document saved to:\n{fp}")

    def _action_open_document(self) -> None:
        fp = filedialog.askopenfilename(filetypes=[("SoftWork Documents", "*.softwork")])
        if fp:
            self.document = load_document(fp)
            self.agent = CADAgent(self.document)
            self.document.add_change_listener(self._on_document_changed)
            self._refresh_all()

    def _action_new_document(self) -> None:
        self.document = Document(name="Untitled.softwork")
        self.agent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)
        self._refresh_all()
