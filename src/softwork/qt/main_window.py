"""
SoftWork PySide6 / Qt6 Desktop CAD IDE Main Window (PTC Creo & SolidWorks Architecture).
"""
from __future__ import annotations
from typing import Optional, Dict, Any

from softwork.ai.agent import CADAgent, AgentPlan, AgentExecutionResult
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
from softwork.core.feature import Feature, SketchFeature, ExtrudeFeature, RevolveFeature
from softwork.document.serializer import save_document, load_document
from softwork.sketch.plane import StandardPlane
from softwork.qt.styles import DARK_IDE_STYLE
from softwork.qt.viewport import CADQtViewport
from softwork.qt.activity_bar import QtActivityBar
from softwork.qt.floating_copilot import QtFloatingCopilot

try:
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QSplitter,
        QTreeWidget,
        QTreeWidgetItem,
        QLabel,
        QLineEdit,
        QPushButton,
        QToolBar,
        QStatusBar,
        QMessageBox,
        QFileDialog,
        QFrame,
        QScrollArea,
        QTabWidget,
    )
    from PySide6.QtGui import QAction, QIcon, QFont
except ImportError:
    pass


class CADMainWindow(QMainWindow):
    """
    SolidWorks and PTC Creo style desktop CAD IDE window for SoftWork.
    """

    def __init__(self, document: Optional[Document] = None) -> None:
        super().__init__()
        self.setWindowTitle("SoftWork CAD — [Part1.softwork *]")
        self.resize(1400, 900)
        self.setMinimumSize(1040, 660)

        # Core Document & Agent
        self.document = document or Document(name="Part1.softwork")
        self.agent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)

        # Apply Modern CAD QSS Styling
        self.setStyleSheet(DARK_IDE_STYLE)

        # Build Clean Desktop CAD Layout
        self._build_menubar()
        self._build_command_manager()
        self._build_central_workspace()
        self._build_statusbar()

        # Seed initial geometry proof
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

    def _build_menubar(self) -> None:
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("File")
        file_menu.addAction("New Part", self._action_new, "Ctrl+N")
        file_menu.addAction("Open Part...", self._action_open, "Ctrl+O")
        file_menu.addAction("Save", self._action_save, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("Export STEP (AP214)...", self._action_export_step)
        file_menu.addAction("Export STL (Binary)...", self._action_export_stl)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit
        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction("Undo", self._action_undo, "Ctrl+Z")
        edit_menu.addAction("Redo", self._action_redo, "Ctrl+Y")

        # Insert / Features
        feat_menu = mb.addMenu("Insert")
        feat_menu.addAction("Boss / Base Extrude...", self._action_extrude)
        feat_menu.addAction("Revolved Boss / Base...", self._action_revolve)
        feat_menu.addAction("Hole Wizard...", self._action_hole_wizard)
        feat_menu.addAction("Fillet...", self._action_fillet)
        feat_menu.addAction("Chamfer...", self._action_chamfer)
        feat_menu.addAction("Linear Pattern...", self._action_pattern)
        feat_menu.addAction("Shell...", self._action_shell)

        # Tools
        tools_menu = mb.addMenu("Tools")
        tools_menu.addAction("Sketch on Front Plane (XY)", lambda: self._action_create_sketch("XY"))
        tools_menu.addAction("Sketch on Top Plane (XZ)", lambda: self._action_create_sketch("XZ"))
        tools_menu.addAction("Sketch on Right Plane (YZ)", lambda: self._action_create_sketch("YZ"))
        tools_menu.addSeparator()
        tools_menu.addAction("Measure Distance & Angle", lambda: None)
        tools_menu.addAction("Mass Properties", lambda: None)

        # View
        view_menu = mb.addMenu("View")
        view_menu.addAction("Zoom to Fit", lambda: self.viewport.reset_view(), "F")
        view_menu.addAction("Isometric View", lambda: self.viewport.set_view_isometric())
        view_menu.addAction("Top View", lambda: self.viewport.set_view_top())
        view_menu.addAction("Front View", lambda: self.viewport.set_view_front())
        view_menu.addAction("Right View", lambda: self.viewport.set_view_right())

        # AI Copilot
        ai_menu = mb.addMenu("Copilot")
        ai_menu.addAction("Toggle Parametric Copilot HUD", self._toggle_copilot)
        ai_menu.addAction("Run Mounting Plate Verification Flow", self._action_demo_flow)

    def _build_command_manager(self) -> None:
        """
        SolidWorks / PTC Creo style CommandManager ribbon bar with clean tabs.
        """
        self.ribbon_tabs = QTabWidget()
        self.ribbon_tabs.setFixedHeight(72)
        self.ribbon_tabs.setObjectName("CommandManager")

        # Tab 1: Features
        features_tb = QToolBar()
        features_tb.setMovable(False)
        features_tb.addAction("Extrude Boss", self._action_extrude)
        features_tb.addAction("Revolve Boss", self._action_revolve)
        features_tb.addSeparator()
        features_tb.addAction("Hole Wizard", self._action_hole_wizard)
        features_tb.addAction("Fillet", self._action_fillet)
        features_tb.addAction("Chamfer", self._action_chamfer)
        features_tb.addAction("Pattern", self._action_pattern)
        features_tb.addAction("Shell", self._action_shell)
        features_tb.addSeparator()
        features_tb.addAction("Plate Primitive", self._action_plate)
        features_tb.addAction("Box Primitive", self._action_box)
        self.ribbon_tabs.addTab(features_tb, "Features")

        # Tab 2: Sketch
        sketch_tb = QToolBar()
        sketch_tb.setMovable(False)
        sketch_tb.addAction("2D Sketch (XY)", lambda: self._action_create_sketch("XY"))
        sketch_tb.addAction("2D Sketch (XZ)", lambda: self._action_create_sketch("XZ"))
        sketch_tb.addAction("2D Sketch (YZ)", lambda: self._action_create_sketch("YZ"))
        sketch_tb.addSeparator()
        sketch_tb.addAction("Corner Rectangle", lambda: self.viewport.set_tool_mode("DRAW_RECTANGLE", self.viewport.active_sketch_plane))
        sketch_tb.addAction("Center Circle", lambda: self.viewport.set_tool_mode("DRAW_CIRCLE", self.viewport.active_sketch_plane))
        sketch_tb.addAction("Select Tool", lambda: self.viewport.set_tool_mode("SELECT"))
        self.ribbon_tabs.addTab(sketch_tb, "Sketch")

        # Tab 3: Evaluate
        eval_tb = QToolBar()
        eval_tb.setMovable(False)
        eval_tb.addAction("Measure", lambda: None)
        eval_tb.addAction("Mass Properties", lambda: None)
        eval_tb.addAction("Section View", lambda: None)
        self.ribbon_tabs.addTab(eval_tb, "Evaluate")

        # Tab 4: Parametric Copilot
        copilot_tb = QToolBar()
        copilot_tb.setMovable(False)
        copilot_tb.addAction("Toggle Copilot HUD", self._toggle_copilot)
        copilot_tb.addAction("Run Demo Flow", self._action_demo_flow)
        self.ribbon_tabs.addTab(copilot_tb, "Parametric Copilot")

        # Tab 5: Data & Export
        data_tb = QToolBar()
        data_tb.setMovable(False)
        data_tb.addAction("Save .softwork", self._action_save)
        data_tb.addAction("Export STEP", self._action_export_step)
        data_tb.addAction("Export STL", self._action_export_stl)
        data_tb.addSeparator()
        data_tb.addAction("Undo", self._action_undo)
        data_tb.addAction("Redo", self._action_redo)
        self.ribbon_tabs.addTab(data_tb, "I/O & History")

    def _build_central_workspace(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_v_layout = QVBoxLayout(central)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)

        # Add CommandManager at the top
        main_v_layout.addWidget(self.ribbon_tabs)

        workspace_h_layout = QHBoxLayout()
        workspace_h_layout.setContentsMargins(0, 0, 0, 0)
        workspace_h_layout.setSpacing(0)
        main_v_layout.addLayout(workspace_h_layout, 1)

        # 1. Activity Bar (Far Left)
        self.activity_bar = QtActivityBar(central)
        self.activity_bar.tabChanged.connect(self._on_activity_tab)
        self.activity_bar.aiClicked.connect(self._toggle_copilot)
        workspace_h_layout.addWidget(self.activity_bar)

        # 2. Main Horizontal Splitter
        splitter = QSplitter(Qt.Horizontal, central)
        splitter.setHandleWidth(2)
        workspace_h_layout.addWidget(splitter, 1)

        # Left Sidebar: FeatureManager Design Tree (Model Tree)
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(4)

        lbl_tree = QLabel("FEATUREMANAGER DESIGN TREE")
        lbl_tree.setStyleSheet("color: #8B949E; font-weight: 700; font-size: 10px; letter-spacing: 0.5px;")
        left_layout.addWidget(lbl_tree)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Feature / Item", "Type", "Status"])
        self.tree.itemSelectionChanged.connect(self._on_tree_select)
        left_layout.addWidget(self.tree)
        splitter.addWidget(self.left_panel)

        # Center: 3D Viewport with Floating Copilot HUD Overlaid
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Breadcrumb Bar
        bc_frame = QFrame()
        bc_frame.setStyleSheet("background-color: #21252B; border-bottom: 1px solid #2C313A; padding: 2px 6px;")
        bc_layout = QHBoxLayout(bc_frame)
        bc_layout.setContentsMargins(4, 2, 4, 2)
        self.lbl_breadcrumb = QLabel("Part1 (Default) > Solid Body > Active Geometry")
        self.lbl_breadcrumb.setStyleSheet("color: #8B949E; font-size: 11px;")
        bc_layout.addWidget(self.lbl_breadcrumb)
        bc_layout.addStretch()
        center_layout.addWidget(bc_frame)

        # 3D Viewport
        self.viewport = CADQtViewport(center_widget)
        self.viewport.faceSelected.connect(self._on_face_picked)
        center_layout.addWidget(self.viewport, 1)

        # Draggable Floating Copilot HUD Overlaid on Viewport
        self.floating_copilot = QtFloatingCopilot(self.viewport, agent=self.agent)
        self.floating_copilot.planPreviewRequested.connect(self._on_copilot_preview)
        self.floating_copilot.promptExecuted.connect(self._on_copilot_executed)
        self.floating_copilot.move(18, 44)

        splitter.addWidget(center_widget)

        # Right Sidebar: PropertyManager Inspector
        self.right_panel = QWidget()
        self.right_panel.setFixedWidth(280)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(4)

        lbl_props = QLabel("PROPERTYMANAGER")
        lbl_props.setStyleSheet("color: #8B949E; font-weight: 700; font-size: 10px; letter-spacing: 0.5px;")
        right_layout.addWidget(lbl_props)

        self.props_container = QWidget()
        self.props_layout = QVBoxLayout(self.props_container)
        self.props_layout.setContentsMargins(0, 0, 0, 0)
        self.props_layout.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.props_container)
        scroll.setStyleSheet("background-color: #1E2227; border: 1px solid #2C313A;")
        right_layout.addWidget(scroll)

        splitter.addWidget(self.right_panel)

    def _build_statusbar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_mode = QLabel("Editing Part")
        self.lbl_status_mode.setStyleSheet("color: #00A8FF; font-weight: 600; padding-right: 12px;")
        self.status_bar.addWidget(self.lbl_status_mode)

        self.lbl_status_coords = QLabel("X: 0.00 mm  Y: 0.00 mm  Z: 0.00 mm")
        self.lbl_status_coords.setStyleSheet("color: #8B949E; padding-right: 16px;")
        self.status_bar.addWidget(self.lbl_status_coords)

        self.lbl_status_units = QLabel("MMGS (mm, g, s)")
        self.lbl_status_units.setStyleSheet("color: #DCE1E8; padding-right: 12px; font-weight: 600;")
        self.status_bar.addPermanentWidget(self.lbl_status_units)

        self.lbl_status_rebuild = QLabel("[Rebuilt: Clean]")
        self.lbl_status_rebuild.setStyleSheet("color: #98C379; font-weight: 600;")
        self.status_bar.addPermanentWidget(self.lbl_status_rebuild)

    def _toggle_copilot(self) -> None:
        self.floating_copilot.setVisible(not self.floating_copilot.isVisible())

    def _on_activity_tab(self, tab_id: str) -> None:
        if tab_id == "tree":
            self.left_panel.setVisible(True)
        elif tab_id == "props":
            self.right_panel.setVisible(True)
        elif tab_id == "tools":
            self.ribbon_tabs.setCurrentIndex(0)

    def _on_copilot_preview(self, plan: AgentPlan) -> None:
        if plan.ghost_mesh:
            self.viewport.set_ghost_mesh(plan.ghost_mesh, delta_vol=plan.predicted_delta_vol)

    def _on_copilot_executed(self, result: AgentExecutionResult) -> None:
        if result.success:
            self.status_bar.showMessage(f"Copilot: {result.explanation}", 6000)
        else:
            self.status_bar.showMessage(f"Error: {result.error_message}", 8000)
        self._refresh_all()

    def _on_face_picked(self, face_idx: int, normal: tuple) -> None:
        self.status_bar.showMessage(f"Selected Face #{face_idx} | Normal: ({normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f})", 5000)

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

        # Update Tree (SolidWorks / Creo hierarchy with Datums)
        self.tree.clear()
        part_item = QTreeWidgetItem([f"{self.document.name} (Default)", "Part", "Active"])
        self.tree.addTopLevelItem(part_item)

        # Standard Datums
        part_item.addChild(QTreeWidgetItem(["Front Plane", "DatumPlane", "Fixed"]))
        part_item.addChild(QTreeWidgetItem(["Top Plane", "DatumPlane", "Fixed"]))
        part_item.addChild(QTreeWidgetItem(["Right Plane", "DatumPlane", "Fixed"]))
        part_item.addChild(QTreeWidgetItem(["Origin", "CoordinateOrigin", "Fixed"]))

        # Features
        for feat in self.document.active_part.features:
            feat_item = QTreeWidgetItem([feat.name, feat.feature_type.value, feat.status.value])
            part_item.addChild(feat_item)
            if isinstance(feat, ExtrudeFeature) or isinstance(feat, RevolveFeature):
                sk_id = getattr(feat, "sketch_feature_id", None)
                if sk_id:
                    sk_node = self.document.get_feature(sk_id)
                    if sk_node:
                        feat_item.addChild(QTreeWidgetItem([f"(-) {sk_node.name}", "SketchProfile", "UnderDefined"]))

        self.tree.expandAll()

        # Update Breadcrumbs
        feat_name = self.document.active_part.features[-1].name if self.document.active_part.features else "Empty"
        self.lbl_breadcrumb.setText(f"{self.document.name} > {self.document.active_part.name} > {feat_name}")

        self._refresh_properties()

        vol = solid.volume if solid else 0.0
        self.status_bar.showMessage(f"Solid Valid | Volume: {vol:,.1f} mm³ | Features: {len(self.document.active_part.features)}")

    def _refresh_properties(self) -> None:
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        feat_id = self.document.selection.primary_feature_id
        if not feat_id and self.document.active_part.features:
            feat_id = self.document.active_part.features[-1].id

        feature = self.document.get_feature(feat_id) if feat_id else None
        if not feature:
            lbl = QLabel("No feature selected")
            lbl.setStyleSheet("color: #8B949E;")
            self.props_layout.addWidget(lbl)
            return

        lbl_f = QLabel(f"Feature: {feature.name}")
        lbl_f.setStyleSheet("color: #00A8FF; font-weight: 700; font-size: 11px;")
        self.props_layout.addWidget(lbl_f)

        lbl_t = QLabel(f"Type: {feature.feature_type.value.upper()}")
        lbl_t.setStyleSheet("color: #8B949E; font-size: 10px;")
        self.props_layout.addWidget(lbl_t)

        for param_name, param in feature.parameters.items():
            row = QWidget()
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 2, 0, 2)

            lbl_p = QLabel(f"{param_name.capitalize()}:")
            lbl_p.setFixedWidth(80)
            r_layout.addWidget(lbl_p)

            inp = QLineEdit(str(param.value))
            inp.setFixedWidth(65)
            r_layout.addWidget(inp)

            lbl_u = QLabel(param.unit)
            r_layout.addWidget(lbl_u)

            btn_apply = QPushButton("Apply")
            btn_apply.setFixedWidth(45)
            btn_apply.clicked.connect(lambda _, f=feature.id, p=param_name, e=inp: self._apply_param(f, p, e.text()))
            r_layout.addWidget(btn_apply)

            self.props_layout.addWidget(row)

        self.props_layout.addStretch()

    def _apply_param(self, feat_id: str, param_name: str, val_str: str) -> None:
        try:
            val = float(val_str)
            SetParameterCommand(feat_id, param_name, val).execute(self.document)
        except ValueError:
            QMessageBox.warning(self, "Invalid Value", f"Could not parse '{val_str}' as number.")

    def _on_tree_select(self) -> None:
        pass

    def _action_create_sketch(self, plane: str = "XY") -> None:
        CreateSketchCommand(name=f"Sketch_{plane}", plane_type=StandardPlane(plane)).execute(self.document)
        sk_feat = self.document.active_part.features[-1]
        if isinstance(sk_feat, SketchFeature):
            sk_feat.sketch.add_rectangle(60.0, 40.0, centered=True)
            self.document.recompute()
            self._refresh_all()

    def _action_extrude(self) -> None:
        sk_feat = None
        for f in reversed(self.document.active_part.features):
            if isinstance(f, SketchFeature):
                sk_feat = f
                break
        if not sk_feat:
            self._action_create_sketch("XY")
            sk_feat = self.document.active_part.features[-1]
        if isinstance(sk_feat, SketchFeature):
            ExtrudeSketchCommand(sketch_feature_id=sk_feat.id, distance=25.0).execute(self.document)
            self._refresh_all()

    def _action_revolve(self) -> None:
        sk_feat = None
        for f in reversed(self.document.active_part.features):
            if isinstance(f, SketchFeature):
                sk_feat = f
                break
        if not sk_feat:
            self._action_create_sketch("XY")
            sk_feat = self.document.active_part.features[-1]
        if isinstance(sk_feat, SketchFeature):
            RevolveSketchCommand(sketch_feature_id=sk_feat.id, angle_deg=360.0).execute(self.document)
            self._refresh_all()

    def _action_hole_wizard(self) -> None:
        if not self.document.active_part.features:
            self._action_plate()
        target = self.document.active_part.features[0]
        AddHoleWizardCommand(target_feature_id=target.id, metric_size="M8", hole_type="counterbore", depth=25.0).execute(self.document)
        self._refresh_all()

    def _action_fillet(self) -> None:
        if self.document.active_part.features:
            feat = self.document.active_part.features[0]
            AddFilletCommand(target_feature_id=feat.id, radius=2.0).execute(self.document)
            self._refresh_all()

    def _action_shell(self) -> None:
        if not self.document.active_part.features:
            self._action_box()
        target = self.document.active_part.features[0]
        AddShellCommand(target_feature_id=target.id, wall_thickness=2.0).execute(self.document)
        self._refresh_all()

    def _action_pattern(self) -> None:
        if self.document.active_part.features:
            feat = self.document.active_part.features[-1]
            AddPatternCommand(target_feature_id=feat.id, count_x=3, count_y=1, spacing_x=30.0).execute(self.document)
            self._refresh_all()

    def _action_chamfer(self) -> None:
        if self.document.active_part.features:
            feat = self.document.active_part.features[0]
            AddChamferCommand(target_feature_id=feat.id, distance=1.5).execute(self.document)
            self._refresh_all()

    def _action_box(self) -> None:
        CreateBoxCommand(width=100.0, height=60.0, depth=10.0).execute(self.document)
        self._refresh_all()

    def _action_plate(self) -> None:
        CreateMountingPlateCommand(length=100.0, width=60.0, thickness=10.0, hole_diameter=8.0, hole_offset=10.0, fillet_radius=2.0).execute(self.document)
        self._refresh_all()

    def _action_undo(self) -> None:
        if self.document.history.can_undo:
            self.document.history.undo()
            self.document.recompute()
            self._refresh_all()

    def _action_redo(self) -> None:
        if self.document.history.can_redo:
            self.document.history.redo()
            self.document.recompute()
            self._refresh_all()

    def _action_export_step(self) -> None:
        solid = self.document.active_part.active_solid
        if not solid:
            QMessageBox.warning(self, "Export", "No active solid geometry.")
            return
        fp, _ = QFileDialog.getSaveFileName(self, "Export STEP", "", "STEP Files (*.step *.stp)")
        if fp:
            self.document.backend.export_step(solid, fp)
            QMessageBox.information(self, "Exported", f"STEP exported to {fp}")

    def _action_export_stl(self) -> None:
        solid = self.document.active_part.active_solid
        if not solid:
            QMessageBox.warning(self, "Export", "No active solid geometry.")
            return
        fp, _ = QFileDialog.getSaveFileName(self, "Export STL", "", "STL Files (*.stl)")
        if fp:
            self.document.backend.export_stl(solid, fp, binary=True)
            QMessageBox.information(self, "Exported", f"STL exported to {fp}")

    def _action_save(self) -> None:
        fp, _ = QFileDialog.getSaveFileName(self, "Save Document", "", "SoftWork (*.softwork)")
        if fp:
            save_document(self.document, fp)
            QMessageBox.information(self, "Saved", f"Saved to {fp}")

    def _action_open(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "SoftWork (*.softwork)")
        if fp:
            self.document = load_document(fp)
            self.agent = CADAgent(self.document)
            self.document.add_change_listener(self._on_document_changed)
            self._refresh_all()

    def _action_new(self) -> None:
        self.document = Document(name="Part1.softwork")
        self.agent = CADAgent(self.document)
        self.document.add_change_listener(self._on_document_changed)
        self._refresh_all()

    def _action_demo_flow(self) -> None:
        self.agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.agent.execute_prompt("Add four M8 holes, 10 mm from each corner")
        self.agent.execute_prompt("Fillet the outer edges by 2 mm")
        self._refresh_all()
        QMessageBox.information(self, "Workflow Completed", "Parametric CAD model generated successfully.")
