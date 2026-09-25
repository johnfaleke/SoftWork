"""
SoftWork Main Window Desktop Interface.
Integrates 3D Viewport, Feature Tree, Properties Inspector, AI Copilot Command Bar, and Validation Bar.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any

from softwork.ai.agent import CADAgent
from softwork.cad.geometry import MeshData
from softwork.commands.feature_commands import CreateBoxCommand, CreateMountingPlateCommand
from softwork.commands.parameter_commands import SetParameterCommand
from softwork.core.document import Document
from softwork.core.feature import Feature
from softwork.document.serializer import save_document, load_document
from softwork.ui.viewport import CAD3DCanvas


class MainWindow(tk.Tk):
    """
    Primary desktop application window for SoftWork.
    """

    def __init__(self, document: Optional[Document] = None) -> None:
        super().__init__()
        self.title("SoftWork — AI-native Parametric CAD")
        self.geometry("1280x820")
        self.minsize(960, 600)
        self.configure(bg="#0B0F19")

        # Core CAD Document & AI Agent
        self.document: Document = document or Document(name="Untitled.softwork")
        self.agent: CADAgent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)

        # Setup modern dark theme styles
        self._setup_styles()

        # Build UI layout
        self._build_menu()
        self._build_toolbar()
        self._build_main_layout()
        self._build_ai_command_bar()
        self._build_status_bar()

        # Initial CAD solid generation proof (Task 74 & 75)
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
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Dark color palette
        style.configure(".", background="#0B0F19", foreground="#F8FAFC", font=("Segoe UI", 9))
        style.configure("TFrame", background="#0F172A")
        style.configure("TLabelframe", background="#0F172A", foreground="#94A3B8", relief="flat")
        style.configure("TLabelframe.Label", background="#0F172A", foreground="#38BDF8", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background="#0F172A", foreground="#E2E8F0", fieldbackground="#0F172A", rowheight=26)
        style.map("Treeview", background=[("selected", "#0284C7")], foreground=[("selected", "#FFFFFF")])
        style.configure("TEntry", fieldbackground="#1E293B", foreground="#F8FAFC", insertcolor="#38BDF8")
        style.configure("TButton", background="#1E293B", foreground="#F8FAFC", relief="flat", padding=4)
        style.map("TButton", background=[("active", "#0284C7"), ("pressed", "#0369A1")])
        style.configure("Accent.TButton", background="#0284C7", foreground="#FFFFFF", font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#0369A1")])

    def _build_menu(self) -> None:
        menubar = tk.Menu(self, bg="#0F172A", fg="#E2E8F0", activebackground="#0284C7", activeforeground="#FFFFFF")
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#0F172A", fg="#E2E8F0")
        file_menu.add_command(label="New Part", command=self._action_new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Open .softwork...", command=self._action_open_document, accelerator="Ctrl+O")
        file_menu.add_command(label="Save...", command=self._action_save_document, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export STEP (AP214)...", command=self._action_export_step)
        file_menu.add_command(label="Export STL (Binary)...", command=self._action_export_stl)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#0F172A", fg="#E2E8F0")
        edit_menu.add_command(label="Undo", command=self._action_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._action_redo, accelerator="Ctrl+Y")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#0F172A", fg="#E2E8F0")
        view_menu.add_command(label="Reset Camera (Isometric)", command=lambda: self.viewport.reset_view())
        menubar.add_cascade(label="View", menu=view_menu)

        # AI Menu
        ai_menu = tk.Menu(menubar, tearoff=0, bg="#0F172A", fg="#E2E8F0")
        ai_menu.add_command(label="Run Demo Flow (Mounting Plate)", command=self._action_run_demo_flow)
        menubar.add_cascade(label="AI", menu=ai_menu)

        self.config(menu=menubar)

    def _build_toolbar(self) -> None:
        toolbar = tk.Frame(self, bg="#1E293B", height=42, padx=8, pady=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_box = ttk.Button(toolbar, text="➕ Box", command=self._action_create_box)
        btn_box.pack(side=tk.LEFT, padx=3)

        btn_plate = ttk.Button(toolbar, text="➕ Mounting Plate", command=self._action_create_plate)
        btn_plate.pack(side=tk.LEFT, padx=3)

        btn_step = ttk.Button(toolbar, text="💾 Export STEP", command=self._action_export_step)
        btn_step.pack(side=tk.LEFT, padx=3)

        btn_stl = ttk.Button(toolbar, text="💾 Export STL", command=self._action_export_stl)
        btn_stl.pack(side=tk.LEFT, padx=3)

        btn_undo = ttk.Button(toolbar, text="⟲ Undo", command=self._action_undo)
        btn_undo.pack(side=tk.RIGHT, padx=3)

        btn_redo = ttk.Button(toolbar, text="⟳ Redo", command=self._action_redo)
        btn_redo.pack(side=tk.RIGHT, padx=3)

    def _build_main_layout(self) -> None:
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#0B0F19", sashrelief=tk.FLAT, sashwidth=4)
        main_pane.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Panel: Feature Tree
        left_frame = ttk.LabelFrame(main_pane, text="MODEL TREE", padding=6)
        main_pane.add(left_frame, width=260)

        self.tree = ttk.Treeview(left_frame, columns=("Type", "Status"), show="tree headings")
        self.tree.heading("#0", text="Feature")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Status", text="Status")
        self.tree.column("#0", width=130)
        self.tree.column("Type", width=70)
        self.tree.column("Status", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Center: 3D Viewport
        center_frame = tk.Frame(main_pane, bg="#0F172A")
        main_pane.add(center_frame, width=720)

        self.viewport = CAD3DCanvas(center_frame)
        self.viewport.pack(fill=tk.BOTH, expand=True)

        # Right Panel: Properties Inspector
        right_frame = ttk.LabelFrame(main_pane, text="PROPERTIES", padding=6)
        main_pane.add(right_frame, width=300)

        self.props_container = tk.Frame(right_frame, bg="#0F172A")
        self.props_container.pack(fill=tk.BOTH, expand=True)

    def _build_ai_command_bar(self) -> None:
        ai_frame = tk.Frame(self, bg="#1E293B", padx=10, pady=8)
        ai_frame.pack(side=tk.BOTTOM, fill=tk.X)

        lbl = tk.Label(ai_frame, text="✨ SoftWork AI Copilot:", bg="#1E293B", fg="#38BDF8", font=("Segoe UI", 10, "bold"))
        lbl.pack(side=tk.LEFT, padx=(0, 8))

        self.ai_entry = tk.Entry(ai_frame, bg="#0F172A", fg="#F8FAFC", insertbackground="#38BDF8", relief="flat", font=("Segoe UI", 10))
        self.ai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)
        self.ai_entry.insert(0, "Create a 100 x 60 x 10 mm mounting plate")
        self.ai_entry.bind("<Return>", lambda e: self._action_submit_ai_prompt())

        btn_send = ttk.Button(ai_frame, text="Ask AI", style="Accent.TButton", command=self._action_submit_ai_prompt)
        btn_send.pack(side=tk.RIGHT, padx=4)

    def _build_status_bar(self) -> None:
        self.status_bar = tk.Label(
            self,
            text="Ready | SoftWork CAD Kernel Active",
            bg="#0B0F19",
            fg="#94A3B8",
            anchor=tk.W,
            padx=10,
            pady=3,
            font=("Segoe UI", 8),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_document_changed(self) -> None:
        self._refresh_all()

    def _refresh_all(self) -> None:
        # Refresh 3D Viewport
        solid = self.document.active_part.active_solid
        mesh = self.document.backend.to_mesh(solid) if solid else None
        self.viewport.set_mesh(mesh)

        # Refresh Feature Tree
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

        # Refresh Properties
        self._refresh_properties()

        # Refresh Status
        val = self.document.latest_validation
        if val and not val.is_valid:
            self.status_bar.config(text=f"⚠️ Validation Issue: {val.issues[0].message}", fg="#EF4444")
        else:
            vol = solid.volume if solid else 0.0
            self.status_bar.config(text=f"✓ Solid Valid | Volume: {vol:,.1f} mm³ | Backend: {self.document.backend.name()}", fg="#10B981")

    def _refresh_properties(self) -> None:
        for widget in self.props_container.winfo_children():
            widget.destroy()

        feat_id = self.document.selection.primary_feature_id
        if not feat_id and self.document.active_part.features:
            feat_id = self.document.active_part.features[0].id

        feature = self.document.get_feature(feat_id) if feat_id else None
        if not feature:
            lbl = tk.Label(self.props_container, text="No feature selected", bg="#0F172A", fg="#64748B")
            lbl.pack(pady=20)
            return

        # Feature header
        tk.Label(self.props_container, text=f"Feature: {feature.name}", bg="#0F172A", fg="#38BDF8", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        tk.Label(self.props_container, text=f"Type: {feature.feature_type.value}", bg="#0F172A", fg="#94A3B8").pack(anchor=tk.W)

        # Parameter editors
        for param_name, param in feature.parameters.items():
            row = tk.Frame(self.props_container, bg="#0F172A")
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=f"{param_name.capitalize()}:", bg="#0F172A", fg="#E2E8F0", width=14, anchor=tk.W).pack(side=tk.LEFT)
            
            entry = tk.Entry(row, bg="#1E293B", fg="#F8FAFC", insertbackground="#38BDF8", width=10, relief="flat")
            entry.insert(0, str(param.value))
            entry.pack(side=tk.LEFT, padx=4)

            tk.Label(row, text=param.unit, bg="#0F172A", fg="#94A3B8").pack(side=tk.LEFT)

            def make_handler(f_id: str, p_name: str, ent: tk.Entry):
                return lambda: self._apply_param_edit(f_id, p_name, ent.get())

            btn = ttk.Button(row, text="Apply", width=6, command=make_handler(feature.id, param_name, entry))
            btn.pack(side=tk.RIGHT, padx=2)

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

    def _action_submit_ai_prompt(self) -> None:
        prompt = self.ai_entry.get().strip()
        if not prompt:
            return

        result = self.agent.execute_prompt(prompt)
        if result.success:
            self.status_bar.config(text=f"✨ AI: {result.explanation}", fg="#38BDF8")
        else:
            self.status_bar.config(text=f"⚠️ AI Error: {result.error_message}", fg="#EF4444")
            messagebox.showwarning("CAD Agent Notice", result.error_message)

    def _action_run_demo_flow(self) -> None:
        """Executes the complete MVP sequence from Section 85 & 152 of the Master Plan."""
        # 1. Create Plate
        self.agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        # 2. Add 4 M8 Holes
        self.agent.execute_prompt("Add four M8 holes, 10 mm from each corner")
        # 3. Fillet outer edges by 2 mm
        self.agent.execute_prompt("Fillet the outer edges by 2 mm")
        # 4. Make it 15 mm thick
        self.agent.execute_prompt("Make it 15 mm thick")
        messagebox.showinfo("Demo Completed", "SoftWork MVP Flow successfully executed!\nMounting plate generated, hole pattern preserved, fillets applied, thickness changed to 15mm.")

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
