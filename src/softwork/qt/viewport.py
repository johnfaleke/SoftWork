"""
Modern High-Performance 3D CAD Viewport for SoftWork Qt6 IDE.
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
    )
except ImportError:
    pass


class CADQtViewport(QWidget):
    """
    Hardware-accelerated, high-fidelity 3D Viewport canvas for PySide6 CAD IDE.
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

        # HUD Quick View Buttons [(label, rect, action)]
        self._hud_buttons: List[Tuple[str, QRect, Callable[[], None]]] = []

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

        # Background (Deep pitch black canvas)
        painter.fillRect(0, 0, w, h, QColor("#080808"))

        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        # 1. Sleek CAD Ground Grid
        grid_size = 140.0
        grid_step = 20.0
        for g in range(-int(grid_size), int(grid_size) + 1, int(grid_step)):
            is_major = (g == 0)
            pen_color = QColor("#282828") if is_major else QColor("#141414")
            painter.setPen(QPen(pen_color, 1))

            p1 = self._project_point(-grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            p2 = self._project_point(grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

            p3 = self._project_point(g, -grid_size, 0.0, cx, cy, rad_x, rad_y)
            p4 = self._project_point(g, grid_size, 0.0, cx, cy, rad_x, rad_y)
            painter.drawLine(int(p3[0]), int(p3[1]), int(p4[0]), int(p4[1]))

        # 2. Render 3D Solid Geometry
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
                    diffuse = max(0.2, nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2])
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
                    face_color = QColor("#FFB800")
                    border_color = QColor("#FFE066")
                    pen_w = 2
                else:
                    # High contrast electric cyan solid with diffuse shading
                    r = int(min(255, max(10, 0 * diff)))
                    g = int(min(255, max(40, 240 * diff)))
                    b = int(min(255, max(50, 255 * diff)))
                    face_color = QColor(r, g, b)
                    border_color = QColor("#007788")
                    pen_w = 1

                qpoly = QPolygonF([QPoint(int(v0[0]), int(v0[1])), QPoint(int(v1[0]), int(v1[1])), QPoint(int(v2[0]), int(v2[1]))])
                painter.setBrush(QBrush(face_color))
                painter.setPen(QPen(border_color, pen_w))
                painter.drawPolygon(qpoly)

            # Draw crisp wireframe edges
            if self._mesh.edges:
                painter.setPen(QPen(QColor("#00F0FF"), 1.5))
                for edge in self._mesh.edges:
                    v0 = projected_verts[edge[0]]
                    v1 = projected_verts[edge[1]]
                    painter.drawLine(int(v0[0]), int(v0[1]), int(v1[0]), int(v1[1]))

        # 2.5 AI Ghost Preview Mesh
        if self._ghost_mesh and self._ghost_mesh.vertices:
            ghost_proj = []
            for gv in self._ghost_mesh.vertices:
                ghost_proj.append(self._project_point(gv[0], gv[1], gv[2], cx, cy, rad_x, rad_y))

            ghost_pen = QPen(QColor("#FFB800"), 1, Qt.DashLine)
            painter.setPen(ghost_pen)
            painter.setBrush(Qt.NoBrush)
            for f in self._ghost_mesh.faces:
                gv0, gv1, gv2 = ghost_proj[f[0]], ghost_proj[f[1]], ghost_proj[f[2]]
                qpoly = QPolygonF([QPoint(int(gv0[0]), int(gv0[1])), QPoint(int(gv1[0]), int(gv1[1])), QPoint(int(gv2[0]), int(gv2[1]))])
                painter.drawPolygon(qpoly)

            # AI Ghost Badge
            badge_rect = QRect(w - 180, 16, 165, 42)
            painter.setBrush(QBrush(QColor("#141414")))
            painter.setPen(QPen(QColor("#FFB800"), 1.5))
            painter.drawRoundedRect(badge_rect, 6, 6)

            painter.setPen(QColor("#FFB800"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.drawText(w - 170, 32, "✨ AI Proposed Shape")

            vol_str = f"{'+' if self._ghost_delta_vol >= 0 else ''}{self._ghost_delta_vol:,.0f} mm³"
            painter.setPen(QColor("#00F0FF"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(w - 170, 48, f"Δ Vol: {vol_str}")

        # 3. Render 2D Sketches
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

                painter.setPen(QPen(QColor("#00FF66"), 2.5))
                n_pts = len(proj_pts)
                is_closed = hasattr(el, "width") or hasattr(el, "radius") or (n_pts > 2)
                for i in range(n_pts if is_closed else n_pts - 1):
                    nxt = (i + 1) % n_pts
                    painter.drawLine(int(proj_pts[i][0]), int(proj_pts[i][1]), int(proj_pts[nxt][0]), int(proj_pts[nxt][1]))

                painter.setBrush(QBrush(QColor("#66FFA6")))
                painter.setPen(QPen(QColor("#008844"), 1))
                for px, py, _ in proj_pts:
                    painter.drawEllipse(QPoint(int(px), int(py)), 3, 3)

        # 4. Viewport HUD Navigation Quick Buttons (Top-Left)
        self._hud_buttons = [
            ("Iso", QRect(14, 14, 40, 24), self.set_view_isometric),
            ("Top", QRect(58, 14, 40, 24), self.set_view_top),
            ("Front", QRect(102, 14, 42, 24), self.set_view_front),
            ("Right", QRect(148, 14, 42, 24), self.set_view_right),
            ("Reset", QRect(194, 14, 44, 24), self.reset_view),
        ]
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for label, rect, _ in self._hud_buttons:
            painter.setBrush(QBrush(QColor("#181818")))
            painter.setPen(QPen(QColor("#2E2E2E"), 1))
            painter.drawRoundedRect(rect, 4, 4)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(rect, Qt.AlignCenter, label)

        # 5. Coordinate Orientation Axes (Bottom-Left)
        axis_cx, axis_cy = 50, h - 50
        axis_len = 30.0
        axes = [
            ("X", 1.0, 0.0, 0.0, QColor("#EF4444")),
            ("Y", 0.0, 1.0, 0.0, QColor("#10B981")),
            ("Z", 0.0, 0.0, 1.0, QColor("#3B82F6")),
        ]
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        for label, ax, ay, az, col in axes:
            p_end = self._project_point(ax * axis_len, ay * axis_len, az * axis_len, axis_cx, axis_cy, rad_x, rad_y)
            ax_x = p_end[0] - self.pan_x
            ax_y = p_end[1] - self.pan_y
            painter.setPen(QPen(col, 2.5))
            painter.drawLine(int(axis_cx), int(axis_cy), int(ax_x), int(ax_y))
            painter.drawText(int(ax_x + 4), int(ax_y), label)

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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta = event.pos() - self._last_mouse_pos
        self._drag_dist += abs(delta.x()) + abs(delta.y())
        self._last_mouse_pos = event.pos()

        if event.buttons() & Qt.RightButton or (event.buttons() & Qt.LeftButton and self._is_panning):
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.update()
        elif event.buttons() & Qt.LeftButton:
            self.rot_y += delta.x() * 0.5
            self.rot_x = max(-89.0, min(89.0, self.rot_x + delta.y() * 0.5))
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
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
