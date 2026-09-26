"""
3D CAD Viewport with interactive Orbit, Pan, Zoom, Lighting, Face/Entity Picking, and Wireframe Shading.
"""
from __future__ import annotations
import math
import tkinter as tk
from typing import Optional, List, Tuple, Dict, Any, Callable

from softwork.cad.geometry import MeshData, BoundingBox, Point3D


class CAD3DCanvas(tk.Canvas):
    """
    High-performance 3D Viewport canvas for desktop CAD visualization.
    Features:
    - 3D perspective & isometric camera
    - Left-click drag: Orbit rotation (Azimuth & Elevation)
    - Right-click drag / Shift+Left drag: Pan (Translation)
    - Mouse wheel / pinch: Zoom
    - Shaded 3D polygonal rasterization with directional diffuse lighting
    - Interactive 3D Face / Surface selection picking (raycasting)
    - Edge highlighting and coordinate orientation axes
    """

    def __init__(
        self,
        master: Any,
        on_face_selected: Optional[Callable[[int, Tuple[float, float, float]], None]] = None,
        on_shape_drawn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> None:
        kwargs.setdefault("bg", "#0F172A")  # Deep slate dark background
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)

        self.on_face_selected = on_face_selected
        self.on_shape_drawn = on_shape_drawn

        # Interaction Tool Mode: "SELECT", "DRAW_RECTANGLE", "DRAW_CIRCLE", "DRAW_LINE"
        self.tool_mode: str = "SELECT"
        self.active_sketch_plane: Optional[Any] = None
        self._draw_start_uv: Optional[Tuple[float, float]] = None
        self._draw_cur_uv: Optional[Tuple[float, float]] = None

        # Camera state
        self.rot_x: float = 30.0  # Elevation (degrees)
        self.rot_y: float = -45.0 # Azimuth (degrees)
        self.zoom: float = 2.8
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0

        # Mouse drag state
        self._last_mouse_x: int = 0
        self._last_mouse_y: int = 0
        self._is_panning: bool = False
        self._drag_dist: float = 0.0

        # Current mesh and sketches to render
        self._mesh: Optional[MeshData] = None
        self._sketches: List[Any] = []
        self._solid_color: str = "#38BDF8"  # Precision CAD cyan/blue
        self.selected_face_idx: Optional[int] = None
        self._rendered_faces: List[Tuple[int, List[Tuple[float, float]], Tuple[float, float, float]]] = []

        # Bind mouse events
        self.bind("<ButtonPress-1>", self._on_left_down)
        self.bind("<B1-Motion>", self._on_left_drag)
        self.bind("<ButtonRelease-1>", self._on_left_up)
        self.bind("<ButtonPress-3>", self._on_right_down)
        self.bind("<B3-Motion>", self._on_right_drag)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Configure>", lambda e: self.render())

    def set_tool_mode(self, mode: str, active_plane: Optional[Any] = None) -> None:
        self.tool_mode = mode
        if active_plane is not None:
            self.active_sketch_plane = active_plane
        self._draw_start_uv = None
        self._draw_cur_uv = None
        self.render()

    def set_mesh(self, mesh: Optional[MeshData], color: str = "#38BDF8") -> None:
        self._mesh = mesh
        self._solid_color = color
        self.selected_face_idx = None
        self.render()

    def set_sketches(self, sketches: List[Any]) -> None:
        self._sketches = sketches or []
        if self._sketches and not self.active_sketch_plane:
            self.active_sketch_plane = getattr(self._sketches[-1], "plane", None)
        self.render()

    def reset_view(self) -> None:
        self.rot_x = 30.0
        self.rot_y = -45.0
        self.zoom = 2.8
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.selected_face_idx = None
        self.render()

    def unproject_to_plane(self, screen_x: float, screen_y: float, plane: Any) -> Tuple[float, float]:
        """Calculates 2D (u, v) on the sketch plane from 2D screen mouse coordinates."""
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        cx, cy = w / 2.0, h / 2.0
        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        x2 = (screen_x - cx - self.pan_x) / max(0.001, self.zoom)
        y2 = -(screen_y - cy - self.pan_y) / max(0.001, self.zoom)

        # Inverse rotation Rx(-rad_x), Ry(-rad_y)
        # 1. Point at z_screen = 0 in camera space
        cos_x, sin_x = math.cos(-rad_x), math.sin(-rad_x)
        cos_y, sin_y = math.cos(-rad_y), math.sin(-rad_y)

        # Vector in camera space: (x2, y2, 0)
        # Ray direction in camera space: (0, 0, 1) -> world ray direction
        rx_d_y = sin_x
        rx_d_z = cos_x
        ray_dx = -sin_y * rx_d_z
        ray_dy = rx_d_y
        ray_dz = cos_y * rx_d_z

        # Ray origin:
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
        if abs(denom) < 1e-6:
            t = 0.0
        else:
            t = (nx * (p0_x - ray_ox) + ny * (p0_y - ray_oy) + nz * (p0_z - ray_oz)) / denom

        hit_x = ray_ox + t * ray_dx
        hit_y = ray_oy + t * ray_dy
        hit_z = ray_oz + t * ray_dz

        rel_x = hit_x - p0_x
        rel_y = hit_y - p0_y
        rel_z = hit_z - p0_z

        u = rel_x * ux + rel_y * uy + rel_z * uz
        v = rel_x * vx + rel_y * vy + rel_z * vz
        return u, v

    def _on_left_down(self, event: tk.Event) -> None:
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self._drag_dist = 0.0
        self._is_panning = bool(event.state & 0x0001)

        if self.tool_mode != "SELECT" and self.active_sketch_plane:
            u, v = self.unproject_to_plane(event.x, event.y, self.active_sketch_plane)
            self._draw_start_uv = (u, v)
            self._draw_cur_uv = (u, v)
            self.render()

    def _on_left_drag(self, event: tk.Event) -> None:
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self._drag_dist += abs(dx) + abs(dy)
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

        if self.tool_mode != "SELECT" and self.active_sketch_plane and self._draw_start_uv:
            u, v = self.unproject_to_plane(event.x, event.y, self.active_sketch_plane)
            self._draw_cur_uv = (u, v)
            self.render()
            return

        if self._is_panning:
            self.pan_x += dx
            self.pan_y += dy
        else:
            self.rot_y += dx * 0.5
            self.rot_x = max(-89.0, min(89.0, self.rot_x + dy * 0.5))

        self.render()

    def _on_left_up(self, event: tk.Event) -> None:
        if self.tool_mode != "SELECT" and self._draw_start_uv and self._draw_cur_uv and self.on_shape_drawn:
            u0, v0 = self._draw_start_uv
            u1, v1 = self._draw_cur_uv
            shape_type = self.tool_mode.replace("DRAW_", "").lower()

            if shape_type == "rectangle":
                w = abs(u1 - u0)
                h = abs(v1 - v0)
                if w > 1.0 and h > 1.0:
                    cu = (u0 + u1) / 2.0
                    cv = (v0 + v1) / 2.0
                    self.on_shape_drawn("rectangle", {"width": w, "height": h, "center_u": cu, "center_v": cv, "centered": True})
            elif shape_type == "circle":
                r = math.hypot(u1 - u0, v1 - v0)
                if r > 1.0:
                    self.on_shape_drawn("circle", {"radius": r, "center_u": u0, "center_v": v0})
            elif shape_type == "line":
                if math.hypot(u1 - u0, v1 - v0) > 1.0:
                    self.on_shape_drawn("line", {"start_u": u0, "start_v": v0, "end_u": u1, "end_v": v1})

            self._draw_start_uv = None
            self._draw_cur_uv = None
            self.render()
            return

        if self._drag_dist < 5.0:
            self._pick_face(event.x, event.y)

    def _on_right_down(self, event: tk.Event) -> None:
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

    def _on_right_drag(self, event: tk.Event) -> None:
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self.pan_x += dx
        self.pan_y += dy
        self.render()

    def _on_wheel(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom = max(0.2, min(50.0, self.zoom * factor))
        self.render()

    def _pick_face(self, mouse_x: int, mouse_y: int) -> None:
        """Finds closest front-facing 2D polygon containing click coordinate."""
        picked_idx = None
        picked_norm = (0.0, 0.0, 1.0)
        # Check rendered faces in reverse depth order (front-most first)
        for face_idx, poly_2d, norm in reversed(self._rendered_faces):
            if self._point_in_triangle(mouse_x, mouse_y, poly_2d[0], poly_2d[1], poly_2d[2]):
                picked_idx = face_idx
                picked_norm = norm
                break

        self.selected_face_idx = picked_idx
        self.render()

        if self.on_face_selected and picked_idx is not None:
            self.on_face_selected(picked_idx, picked_norm)

    def _point_in_triangle(self, px: float, py: float, p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        def sign(p1_x: float, p1_y: float, p2_x: float, p2_y: float, p3_x: float, p3_y: float) -> float:
            return (p1_x - p3_x) * (p2_y - p3_y) - (p2_x - p3_x) * (p1_y - p3_y)

        d1 = sign(px, py, p0[0], p0[1], p1[0], p1[1])
        d2 = sign(px, py, p1[0], p1[1], p2[0], p2[1])
        d3 = sign(px, py, p2[0], p2[1], p0[0], p0[1])
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def _project_point(self, x: float, y: float, z: float, cx: float, cy: float, rad_x: float, rad_y: float) -> Tuple[float, float, float]:
        # 1. Rotate Y (Azimuth)
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x1 = x * cos_y + z * sin_y
        y1 = y
        z1 = -x * sin_y + z * cos_y

        # 2. Rotate X (Elevation)
        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        x2 = x1
        y2 = y1 * cos_x - z1 * sin_x
        z2 = y1 * sin_x + z1 * cos_x

        screen_x = cx + self.pan_x + x2 * self.zoom
        screen_y = cy + self.pan_y - y2 * self.zoom
        return screen_x, screen_y, z2

    def render(self) -> None:
        self.delete("all")
        self._rendered_faces.clear()
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        cx, cy = w / 2.0, h / 2.0

        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        # 1. Subtle CAD workspace grid
        grid_size = 120.0
        grid_step = 20.0
        for g in range(-int(grid_size), int(grid_size) + 1, int(grid_step)):
            p1 = self._project_point(-grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            p2 = self._project_point(grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#1E293B", width=1)

            p3 = self._project_point(g, -grid_size, 0.0, cx, cy, rad_x, rad_y)
            p4 = self._project_point(g, grid_size, 0.0, cx, cy, rad_x, rad_y)
            self.create_line(p3[0], p3[1], p4[0], p4[1], fill="#1E293B", width=1)

        # 2. Render 3D Solid Geometry
        if self._mesh and self._mesh.faces:
            projected_verts: List[Tuple[float, float, float]] = []
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
                    # Highlight selected surface in bright amber/gold
                    color_hex = "#F59E0B"
                    outline_hex = "#FBBF24"
                    outline_w = 2
                else:
                    r_base, g_base, b_base = 56, 189, 248  # #38BDF8
                    r = int(min(255, max(15, r_base * diff)))
                    g = int(min(255, max(30, g_base * diff)))
                    b = int(min(255, max(50, b_base * diff)))
                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                    outline_hex = "#0284C7"
                    outline_w = 1

                self.create_polygon(
                    v0[0], v0[1], v1[0], v1[1], v2[0], v2[1],
                    fill=color_hex,
                    outline=outline_hex,
                    width=outline_w,
                )

            if self._mesh.edges:
                for edge in self._mesh.edges:
                    v0 = projected_verts[edge[0]]
                    v1 = projected_verts[edge[1]]
                    self.create_line(v0[0], v0[1], v1[0], v1[1], fill="#38BDF8", width=1.5)

        # 3. Render 2D Sketches in 3D Space
        for sketch in self._sketches:
            plane = getattr(sketch, "plane", None)
            if not plane:
                continue

            # Draw sketch plane boundary box
            ps_box = [(-60.0, -40.0), (60.0, -40.0), (60.0, 40.0), (-60.0, 40.0)]
            p3_box = [plane.to_3d(u, v, 0.0) for u, v in ps_box]
            proj_box = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in p3_box]
            for bi in range(4):
                bnxt = (bi + 1) % 4
                self.create_line(
                    proj_box[bi][0], proj_box[bi][1], proj_box[bnxt][0], proj_box[bnxt][1],
                    fill="#475569", width=1, dash=(3, 3)
                )

            # Draw sketch elements (lines, rectangles, circles, polygons)
            for el in getattr(sketch, "elements", []):
                pts_2d = el.sample_points(32)
                if not pts_2d:
                    continue
                p3_list = [plane.to_3d(p.u, p.v, 0.0) for p in pts_2d]
                proj_pts = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in p3_list]

                # Draw wire loop
                n_pts = len(proj_pts)
                is_closed_el = hasattr(el, "width") or hasattr(el, "radius") or (n_pts > 2)
                for i in range(n_pts if is_closed_el else n_pts - 1):
                    nxt = (i + 1) % n_pts
                    self.create_line(
                        proj_pts[i][0], proj_pts[i][1], proj_pts[nxt][0], proj_pts[nxt][1],
                        fill="#10B981", width=2.5
                    )

                # Draw vertex dots
                for px, py, _ in proj_pts:
                    self.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#34D399", outline="#065F46", width=1)

            # Draw sketch tag
            tag_p3 = plane.to_3d(0.0, 0.0, 0.0)
            tag_proj = self._project_point(tag_p3.x, tag_p3.y, tag_p3.z, cx, cy, rad_x, rad_y)
            sk_name = getattr(sketch, "name", "Sketch")
            self.create_text(tag_proj[0], tag_proj[1] - 12, text=f"✏️ {sk_name}", fill="#10B981", font=("Segoe UI", 9, "bold"))

        # 3.5 In-progress interactive drawing preview
        if self.tool_mode != "SELECT" and self._draw_start_uv and self._draw_cur_uv and self.active_sketch_plane:
            pl = self.active_sketch_plane
            u0, v0 = self._draw_start_uv
            u1, v1 = self._draw_cur_uv

            if self.tool_mode == "DRAW_RECTANGLE":
                pts_rect = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
                p3_rect = [pl.to_3d(u, v, 0.0) for u, v in pts_rect]
                proj_r = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in p3_rect]
                for ri in range(4):
                    rnxt = (ri + 1) % 4
                    self.create_line(proj_r[ri][0], proj_r[ri][1], proj_r[rnxt][0], proj_r[rnxt][1], fill="#38BDF8", width=2, dash=(4, 2))
                w_mm = abs(u1 - u0)
                h_mm = abs(v1 - v0)
                self.create_text(proj_r[2][0] + 15, proj_r[2][1] - 10, text=f"📐 {w_mm:.1f} × {h_mm:.1f} mm", fill="#38BDF8", font=("Segoe UI", 10, "bold"))

            elif self.tool_mode == "DRAW_CIRCLE":
                r_mm = math.hypot(u1 - u0, v1 - v0)
                circ_pts = []
                for step in range(32):
                    th = 2.0 * math.pi * step / 32
                    cu = u0 + r_mm * math.cos(th)
                    cv = v0 + r_mm * math.sin(th)
                    circ_pts.append(pl.to_3d(cu, cv, 0.0))
                proj_c = [self._project_point(p.x, p.y, p.z, cx, cy, rad_x, rad_y) for p in circ_pts]
                for ci in range(32):
                    cnxt = (ci + 1) % 32
                    self.create_line(proj_c[ci][0], proj_c[ci][1], proj_c[cnxt][0], proj_c[cnxt][1], fill="#38BDF8", width=2, dash=(4, 2))
                cp0 = self._project_point(pl.to_3d(u0, v0, 0.0).x, pl.to_3d(u0, v0, 0.0).y, pl.to_3d(u0, v0, 0.0).z, cx, cy, rad_x, rad_y)
                cp1 = self._project_point(pl.to_3d(u1, v1, 0.0).x, pl.to_3d(u1, v1, 0.0).y, pl.to_3d(u1, v1, 0.0).z, cx, cy, rad_x, rad_y)
                self.create_line(cp0[0], cp0[1], cp1[0], cp1[1], fill="#F59E0B", width=1.5)
                self.create_text(cp1[0] + 12, cp1[1] - 8, text=f"⭕ R = {r_mm:.1f} mm", fill="#38BDF8", font=("Segoe UI", 10, "bold"))

            elif self.tool_mode == "DRAW_LINE":
                lp0 = self._project_point(pl.to_3d(u0, v0, 0.0).x, pl.to_3d(u0, v0, 0.0).y, pl.to_3d(u0, v0, 0.0).z, cx, cy, rad_x, rad_y)
                lp1 = self._project_point(pl.to_3d(u1, v1, 0.0).x, pl.to_3d(u1, v1, 0.0).y, pl.to_3d(u1, v1, 0.0).z, cx, cy, rad_x, rad_y)
                self.create_line(lp0[0], lp0[1], lp1[0], lp1[1], fill="#38BDF8", width=2.5)
                len_mm = math.hypot(u1 - u0, v1 - v0)
                self.create_text(lp1[0] + 12, lp1[1] - 8, text=f"📏 L = {len_mm:.1f} mm", fill="#38BDF8", font=("Segoe UI", 10, "bold"))

        # 4. Coordinate Axes
        axis_cx, axis_cy = 60, h - 60
        axis_len = 35.0
        axes = [
            ("X", 1.0, 0.0, 0.0, "#EF4444"),
            ("Y", 0.0, 1.0, 0.0, "#10B981"),
            ("Z", 0.0, 0.0, 1.0, "#3B82F6"),
        ]
        for label, ax, ay, az, col in axes:
            p_end = self._project_point(ax * axis_len, ay * axis_len, az * axis_len, axis_cx, axis_cy, rad_x, rad_y)
            ax_x = p_end[0] - self.pan_x
            ax_y = p_end[1] - self.pan_y
            self.create_line(axis_cx, axis_cy, ax_x, ax_y, fill=col, width=2.5, arrow=tk.LAST)
            self.create_text(ax_x + 5, ax_y, text=label, fill=col, font=("Segoe UI", 9, "bold"))
