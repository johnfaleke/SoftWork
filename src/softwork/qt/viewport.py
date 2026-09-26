"""
Professional High-Performance 3D CAD Viewport for SoftWork (PTC Creo & SolidWorks aesthetic).
"""
from __future__ import annotations
import math
from typing import Optional, List, Tuple, Dict, Any, Callable

from softwork.cad.geometry import MeshData

try:
    from PySide6.QtCore import Qt, QPoint, QRect, QRectF, Signal
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import (
        QPainter,
        QPen,
        QBrush,
        QColor,
        QPolygonF,
        QPainterPath,
        QFont,
        QMouseEvent,
        QWheelEvent,
        QPaintEvent,
        QLinearGradient,
    )
except ImportError:
    pass


class CADQtViewport(QWidget):
    """
    High-fidelity 3D Viewport canvas for PySide6 CAD IDE.
    Implements SolidWorks and PTC Creo style gradient background, heads-up view toolbar,
    anti-aliased shaded geometry, crisp wireframes, 3D triad, and interactive raycasting.
    """
    faceSelected = Signal(int, tuple)
    shapeDrawn = Signal(str, dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Tool Mode: "SELECT", "DRAW_RECTANGLE", "DRAW_CIRCLE", "DRAW_LINE"
        self.tool_mode: str = "SELECT"
        self.active_sketch_plane: Optional[Any] = None
        self._draw_start_uv: Optional[Tuple[float, float]] = None
        self._draw_cur_uv: Optional[Tuple[float, float]] = None

        # Camera state
        self.rot_x: float = 30.0  # Elevation
        self.rot_y: float = -45.0 # Azimuth
        self.zoom: float = 3.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0

        # Drag state
        self._last_mouse_pos = QPoint()
        self._is_panning: bool = False
        self._drag_dist: float = 0.0

        # Geometry
        self._mesh: Optional[MeshData] = None
        self._ghost_mesh: Optional[MeshData] = None
        self._ghost_delta_vol: float = 0.0
        self._sketches: List[Any] = []
        self.selected_face_idx: Optional[int] = None
        self._rendered_faces: List[Tuple[int, List[Tuple[float, float]], Tuple[float, float, float]]] = []

        # Heads-Up View Toolbar [(label, rect, action)]
        self._hud_buttons: List[Tuple[str, QRect, Callable[[], None]]] = []

    def set_tool_mode(self, mode: str, active_plane: Optional[Any] = None) -> None:
        self.tool_mode = mode
        if active_plane is not None:
            self.active_sketch_plane = active_plane
        self._draw_start_uv = None
        self._draw_cur_uv = None
        self.update()

    def set_mesh(self, mesh: Optional[MeshData]) -> None:
        self._mesh = mesh
        self.selected_face_idx = None
        self._ghost_mesh = None
        self._ghost_delta_vol = 0.0
        self.update()

    def set_ghost_mesh(self, ghost_mesh: Optional[MeshData], delta_vol: float = 0.0) -> None:
        self._ghost_mesh = ghost_mesh
        self._ghost_delta_vol = delta_vol
        self.update()

    def set_sketches(self, sketches: List[Any]) -> None:
        self._sketches = sketches or []
        if self._sketches and not self.active_sketch_plane:
            self.active_sketch_plane = getattr(self._sketches[-1], "plane", None)
        self.update()

    def reset_view(self) -> None:
        self.rot_x = 30.0
        self.rot_y = -45.0
        self.zoom = 3.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.selected_face_idx = None
        self.update()

    def set_view_top(self) -> None:
        self.rot_x = 90.0
        self.rot_y = 0.0
        self.update()

    def set_view_front(self) -> None:
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.update()

    def set_view_right(self) -> None:
        self.rot_x = 0.0
        self.rot_y = -90.0
        self.update()

    def set_view_isometric(self) -> None:
        self.rot_x = 35.264
        self.rot_y = -45.0
        self.update()

    def unproject_to_plane(self, screen_x: float, screen_y: float, plane: Any) -> Tuple[float, float]:
        """Calculates 2D (u, v) on the sketch plane from 2D screen mouse coordinates."""
        w = self.width() or 800
        h = self.height() or 600
        cx, cy = w / 2.0, h / 2.0
        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        x2 = (screen_x - cx - self.pan_x) / max(0.001, self.zoom)
        y2 = -(screen_y - cy - self.pan_y) / max(0.001, self.zoom)

        cos_x, sin_x = math.cos(-rad_x), math.sin(-rad_x)
        cos_y, sin_y = math.cos(-rad_y), math.sin(-rad_y)

        rx_d_y = sin_x
        rx_d_z = cos_x
        ray_dx = -sin_y * rx_d_z
        ray_dy = rx_d_y
        ray_dz = cos_y * rx_d_z

        rx_o_y = y2 * cos_x
        rx_o_z = -y2 * sin_x
        ray_ox = x2 * cos_y + rx_o_z * sin_y
        ray_oy = rx_o_y
        ray_oz = -x2 * sin_y + rx_o_z * cos_y

        p0 = getattr(plane, "origin", None)
        n = getattr(plane, "normal", None)
        u_axis = getattr(plane, "u_axis", None)
        v_axis = getattr(plane, "v_axis", None)

        p0_x = getattr(p0, "x", 0.0)
        p0_y = getattr(p0, "y", 0.0)
        p0_z = getattr(p0, "z", 0.0)
        nx = getattr(n, "x", 0.0)
        ny = getattr(n, "y", 0.0)
        nz = getattr(n, "z", 1.0)
        ux = getattr(u_axis, "x", 1.0)
        uy = getattr(u_axis, "y", 0.0)
        uz = getattr(u_axis, "z", 0.0)
        vx = getattr(v_axis, "x", 0.0)
        vy = getattr(v_axis, "y", 1.0)
        vz = getattr(v_axis, "z", 0.0)

        denom = nx * ray_dx + ny * ray_dy + nz * ray_dz
        t = 0.0 if abs(denom) < 1e-6 else (nx * (p0_x - ray_ox) + ny * (p0_y - ray_oy) + nz * (p0_z - ray_oz)) / denom

        hit_x = ray_ox + t * ray_dx
        hit_y = ray_oy + t * ray_dy
        hit_z = ray_oz + t * ray_dz

        rel_x = hit_x - p0_x
        rel_y = hit_y - p0_y
        rel_z = hit_z - p0_z

        u = rel_x * ux + rel_y * uy + rel_z * uz
        v = rel_x * vx + rel_y * vy + rel_z * vz
        return u, v

    def _project_point(self, x: float, y: float, z: float, cx: float, cy: float, rad_x: float, rad_y: float) -> Tuple[float, float, float]:
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x1 = x * cos_y + z * sin_y
        y1 = y
        z1 = -x * sin_y + z * cos_y

        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        x2 = x1
        y2 = y1 * cos_x - z1 * sin_x
        z2 = y1 * sin_x + z1 * cos_x

        screen_x = cx + self.pan_x + x2 * self.zoom
        screen_y = cy + self.pan_y - y2 * self.zoom
        return screen_x, screen_y, z2

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0

        # Background: Smooth CAD Gradient (SolidWorks / Creo Dark Slate Studio)
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, QColor("#2A2D34"))
        gradient.setColorAt(1.0, QColor("#181A1F"))
        painter.fillRect(0, 0, w, h, gradient)

        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        # 1. Subtle Precision CAD Datum Grid
        grid_size = 140.0
        grid_step = 20.0
        for g in range(-int(grid_size), int(grid_size) + 1, int(grid_step)):
            is_major = (g == 0)
            pen_color = QColor("#3E4451") if is_major else QColor("#22252A")
            painter.setPen(QPen(pen_color, 1))

            p1 = self._project_point(-grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            p2 = self._project_point(grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

            p3 = self._project_point(g, -grid_size, 0.0, cx, cy, rad_x, rad_y)
            p4 = self._project_point(g, grid_size, 0.0, cx, cy, rad_x, rad_y)
            painter.drawLine(int(p3[0]), int(p3[1]), int(p4[0]), int(p4[1]))

        # 2. Render 3D Solid Geometry (CAD Metallic Shaded with Silhouette Edges)
        self._rendered_faces.clear()
        if self._mesh and self._mesh.faces:
            projected_verts = []
            for v in self._mesh.vertices:
                projected_verts.append(self._project_point(v[0], v[1], v[2], cx, cy, rad_x, rad_y))

            face_order = []
            light_dir = (0.577, 0.577, 0.577)

            for i, face in enumerate(self._mesh.faces):
                v0 = projected_verts[face[0]]
                v1 = projected_verts[face[1]]
                v2 = projected_verts[face[2]]
                avg_z = (v0[2] + v1[2] + v2[2]) / 3.0

                o0 = self._mesh.vertices[face[0]]
                o1 = self._mesh.vertices[face[1]]
                o2 = self._mesh.vertices[face[2]]
                ax, ay, az = o1[0] - o0[0], o1[1] - o0[1], o1[2] - o0[2]
                bx, by, bz = o2[0] - o0[0], o2[1] - o0[1], o2[2] - o0[2]
                nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
                norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
                if norm_len > 0:
                    nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len
                    diffuse = max(0.25, nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2])
                else:
                    diffuse = 0.7

                face_order.append((avg_z, i, face, diffuse, (nx, ny, nz)))

            face_order.sort(key=lambda item: item[0])

            for _, face_idx, face, diff, norm in face_order:
                v0 = projected_verts[face[0]]
                v1 = projected_verts[face[1]]
                v2 = projected_verts[face[2]]

                poly_2d = [(v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1])]
                self._rendered_faces.append((face_idx, poly_2d, norm))

                is_selected = (self.selected_face_idx == face_idx)
                if is_selected:
                    # SolidWorks precision cyan selection highlight
                    face_color = QColor("#00A8FF")
                    border_color = QColor("#E0F2FE")
                    pen_w = 2
                else:
                    # Professional CAD neutral titanium surface with diffuse shading
                    base_lum = int(140 * diff + 30)
                    r = min(255, int(base_lum * 0.92))
                    g = min(255, int(base_lum * 0.96))
                    b = min(255, int(base_lum * 1.04))
                    face_color = QColor(r, g, b)
                    border_color = QColor("#22252A")
                    pen_w = 1

                qpoly = QPolygonF([QPoint(int(v0[0]), int(v0[1])), QPoint(int(v1[0]), int(v1[1])), QPoint(int(v2[0]), int(v2[1]))])
                painter.setBrush(QBrush(face_color))
                painter.setPen(QPen(border_color, pen_w))
                painter.drawPolygon(qpoly)

            # Crisp dark silhouette edges (SolidWorks 'Shaded with Edges' mode)
            if self._mesh.edges:
                painter.setPen(QPen(QColor("#181A1F"), 1.2))
                for edge in self._mesh.edges:
                    v0 = projected_verts[edge[0]]
                    v1 = projected_verts[edge[1]]
                    painter.drawLine(int(v0[0]), int(v0[1]), int(v1[0]), int(v1[1]))

        # 2.5 AI Ghost Preview Mesh Overlay
        if self._ghost_mesh and self._ghost_mesh.vertices:
            ghost_proj = []
            for gv in self._ghost_mesh.vertices:
                ghost_proj.append(self._project_point(gv[0], gv[1], gv[2], cx, cy, rad_x, rad_y))

            ghost_pen = QPen(QColor("#00A8FF"), 1, Qt.DashLine)
            painter.setPen(ghost_pen)
            painter.setBrush(Qt.NoBrush)
            for f in self._ghost_mesh.faces:
                gv0, gv1, gv2 = ghost_proj[f[0]], ghost_proj[f[1]], ghost_proj[f[2]]
                qpoly = QPolygonF([QPoint(int(gv0[0]), int(gv0[1])), QPoint(int(gv1[0]), int(gv1[1])), QPoint(int(gv2[0]), int(gv2[1]))])
                painter.drawPolygon(qpoly)

            badge_rect = QRect(w - 190, 14, 175, 40)
            painter.setBrush(QBrush(QColor("#21252B")))
            painter.setPen(QPen(QColor("#00A8FF"), 1))
            painter.drawRoundedRect(badge_rect, 3, 3)

            painter.setPen(QColor("#00A8FF"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.drawText(w - 180, 28, "AI PROPOSED GEOMETRY")

            vol_str = f"{'+' if self._ghost_delta_vol >= 0 else ''}{self._ghost_delta_vol:,.0f} mm³"
            painter.setPen(QColor("#DCE1E8"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(w - 180, 44, f"Predicted Δ Vol: {vol_str}")

        # 3. Render 2D Sketches (SolidWorks Under Defined / Fully Defined Blue/Black lines)
        for sketch in self._sketches:
            plane = getattr(sketch, "plane", None)
            if not plane:
                continue

            for el in getattr(sketch, "elements", []):
                pts_2d = el.sample_points(32)
                if not pts_2d:
                    continue
                p3_list = [plane.to_3d(p.u, p.v, 0.0) for p in pts_2d]
                proj_pts = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in p3_list]

                painter.setPen(QPen(QColor("#007ACC"), 2))
                n_pts = len(proj_pts)
                is_closed = hasattr(el, "width") or hasattr(el, "radius") or (n_pts > 2)
                for i in range(n_pts if is_closed else n_pts - 1):
                    nxt = (i + 1) % n_pts
                    painter.drawLine(int(proj_pts[i][0]), int(proj_pts[i][1]), int(proj_pts[nxt][0]), int(proj_pts[nxt][1]))

                painter.setBrush(QBrush(QColor("#00A8FF")))
                painter.setPen(QPen(QColor("#005A9E"), 1))
                for px, py, _ in proj_pts:
                    painter.drawEllipse(QPoint(int(px), int(py)), 3, 3)

        # 3.5 In-progress interactive drawing preview & Smart Dimension
        if self.tool_mode != "SELECT" and self._draw_start_uv and self._draw_cur_uv and self.active_sketch_plane:
            pl = self.active_sketch_plane
            u0, v0 = self._draw_start_uv
            u1, v1 = self._draw_cur_uv

            if self.tool_mode == "DRAW_RECTANGLE":
                pts_rect = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
                p3_rect = [pl.to_3d(u, v, 0.0) for u, v in pts_rect]
                proj_r = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in p3_rect]
                painter.setPen(QPen(QColor("#00A8FF"), 1.5, Qt.DashLine))
                for ri in range(4):
                    rnxt = (ri + 1) % 4
                    painter.drawLine(int(proj_r[ri][0]), int(proj_r[ri][1]), int(proj_r[rnxt][0]), int(proj_r[rnxt][1]))
                w_mm = abs(u1 - u0)
                h_mm = abs(v1 - v0)
                painter.setPen(QColor("#00A8FF"))
                painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                painter.drawText(int(proj_r[2][0] + 10), int(proj_r[2][1] - 6), f"W: {w_mm:.2f} mm  H: {h_mm:.2f} mm")

        # 4. Heads-Up View Toolbar (Centered Top of Viewport, SolidWorks / Creo style)
        hud_center_x = int(w / 2)
        hud_btn_w = 42
        hud_btn_h = 22
        hud_spacing = 3
        total_hud_w = 7 * hud_btn_w + 6 * hud_spacing
        start_hud_x = hud_center_x - int(total_hud_w / 2)

        self._hud_buttons = [
            ("Fit", QRect(start_hud_x, 10, hud_btn_w, hud_btn_h), self.reset_view),
            ("Iso", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 1, 10, hud_btn_w, hud_btn_h), self.set_view_isometric),
            ("Top", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 2, 10, hud_btn_w, hud_btn_h), self.set_view_top),
            ("Front", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 3, 10, hud_btn_w, hud_btn_h), self.set_view_front),
            ("Right", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 4, 10, hud_btn_w, hud_btn_h), self.set_view_right),
            ("Sect", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 5, 10, hud_btn_w, hud_btn_h), lambda: None),
            ("Style", QRect(start_hud_x + (hud_btn_w + hud_spacing) * 6, 10, hud_btn_w, hud_btn_h), lambda: None),
        ]

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for label, rect, _ in self._hud_buttons:
            painter.setBrush(QBrush(QColor("#21252B")))
            painter.setPen(QPen(QColor("#3E4451"), 1))
            painter.drawRoundedRect(rect, 2, 2)
            painter.setPen(QColor("#DCE1E8"))
            painter.drawText(rect, Qt.AlignCenter, label)

        # 5. 3D Coordinate Triad (Bottom-Left)
        axis_cx, axis_cy = 45, h - 45
        axis_len = 28.0
        axes = [
            ("X", 1.0, 0.0, 0.0, QColor("#E06C75")),
            ("Y", 0.0, 1.0, 0.0, QColor("#98C379")),
            ("Z", 0.0, 0.0, 1.0, QColor("#61AFEF")),
        ]
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for label, ax, ay, az, col in axes:
            p_end = self._project_point(ax * axis_len, ay * axis_len, az * axis_len, axis_cx, axis_cy, rad_x, rad_y)
            ax_x = p_end[0] - self.pan_x
            ax_y = p_end[1] - self.pan_y
            painter.setPen(QPen(col, 2))
            painter.drawLine(int(axis_cx), int(axis_cy), int(ax_x), int(ax_y))
            painter.drawText(int(ax_x + 3), int(ax_y + 3), label)

        # Datum origin circle
        painter.setBrush(QBrush(QColor("#DCE1E8")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(axis_cx, axis_cy), 2, 2)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = event.pos()
        # Check HUD buttons
        for _, rect, action in self._hud_buttons:
            if rect.contains(pos):
                action()
                return

        self._last_mouse_pos = pos
        self._drag_dist = 0.0
        self._is_panning = bool(event.modifiers() & Qt.ShiftModifier)

        if self.tool_mode != "SELECT" and self.active_sketch_plane:
            u, v = self.unproject_to_plane(pos.x(), pos.y(), self.active_sketch_plane)
            self._draw_start_uv = (u, v)
            self._draw_cur_uv = (u, v)
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.pos()
        delta = pos - self._last_mouse_pos
        self._drag_dist += abs(delta.x()) + abs(delta.y())
        self._last_mouse_pos = pos

        if self.tool_mode != "SELECT" and self.active_sketch_plane and self._draw_start_uv:
            u, v = self.unproject_to_plane(pos.x(), pos.y(), self.active_sketch_plane)
            self._draw_cur_uv = (u, v)
            self.update()
            return

        if event.buttons() & Qt.RightButton or (event.buttons() & Qt.LeftButton and self._is_panning):
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.update()
        elif event.buttons() & Qt.LeftButton:
            self.rot_y += delta.x() * 0.5
            self.rot_x = max(-89.0, min(89.0, self.rot_x + delta.y() * 0.5))
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.tool_mode != "SELECT" and self._draw_start_uv and self._draw_cur_uv:
            u0, v0 = self._draw_start_uv
            u1, v1 = self._draw_cur_uv
            shape_type = self.tool_mode.replace("DRAW_", "").lower()

            if shape_type == "rectangle":
                w = abs(u1 - u0)
                h = abs(v1 - v0)
                if w > 1.0 and h > 1.0:
                    cu = (u0 + u1) / 2.0
                    cv = (v0 + v1) / 2.0
                    self.shapeDrawn.emit("rectangle", {"width": w, "height": h, "center_u": cu, "center_v": cv, "centered": True})
            elif shape_type == "circle":
                r = math.hypot(u1 - u0, v1 - v0)
                if r > 1.0:
                    self.shapeDrawn.emit("circle", {"radius": r, "center_u": u0, "center_v": v0})

            self._draw_start_uv = None
            self._draw_cur_uv = None
            self.update()
            return

        if self._drag_dist < 5.0 and event.button() == Qt.LeftButton:
            self._pick_face(event.pos().x(), event.pos().y())

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.zoom = max(0.2, min(50.0, self.zoom * factor))
        self.update()

    def _pick_face(self, mouse_x: int, mouse_y: int) -> None:
        picked_idx = None
        picked_norm = (0.0, 0.0, 1.0)
        for face_idx, poly_2d, norm in reversed(self._rendered_faces):
            p0, p1, p2 = poly_2d[0], poly_2d[1], poly_2d[2]
            if self._point_in_triangle(mouse_x, mouse_y, p0, p1, p2):
                picked_idx = face_idx
                picked_norm = norm
                break

        self.selected_face_idx = picked_idx
        self.update()

        if picked_idx is not None:
            self.faceSelected.emit(picked_idx, picked_norm)

    def _point_in_triangle(self, px: float, py: float, p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        def sign(p1_x: float, p1_y: float, p2_x: float, p2_y: float, p3_x: float, p3_y: float) -> float:
            return (p1_x - p3_x) * (p2_y - p3_y) - (p2_x - p3_x) * (p1_y - p3_y)

        d1 = sign(px, py, p0[0], p0[1], p1[0], p1[1])
        d2 = sign(px, py, p1[0], p1[1], p2[0], p2[1])
        d3 = sign(px, py, p2[0], p2[1], p0[0], p0[1])
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)
