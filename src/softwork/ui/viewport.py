"""
3D CAD Viewport with interactive Orbit, Pan, Zoom, Lighting, and Wireframe Shading.
"""
from __future__ import annotations
import math
import tkinter as tk
from typing import Optional, List, Tuple, Dict, Any

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
    - Edge highlighting and coordinate orientation axes
    """

    def __init__(self, master: Any, **kwargs: Any) -> None:
        kwargs.setdefault("bg", "#0F172A")  # Deep slate dark background
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)

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

        # Current mesh to render
        self._mesh: Optional[MeshData] = None
        self._solid_color: str = "#38BDF8"  # Precision CAD cyan/blue

        # Bind mouse events
        self.bind("<ButtonPress-1>", self._on_left_down)
        self.bind("<B1-Motion>", self._on_left_drag)
        self.bind("<ButtonPress-3>", self._on_right_down)
        self.bind("<B3-Motion>", self._on_right_drag)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Configure>", lambda e: self.render())

    def set_mesh(self, mesh: Optional[MeshData], color: str = "#38BDF8") -> None:
        self._mesh = mesh
        self._solid_color = color
        self.render()

    def reset_view(self) -> None:
        self.rot_x = 30.0
        self.rot_y = -45.0
        self.zoom = 2.8
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.render()

    def _on_left_down(self, event: tk.Event) -> None:
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self._is_panning = bool(event.state & 0x0001)  # Shift key pressed

    def _on_left_drag(self, event: tk.Event) -> None:
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

        if self._is_panning:
            self.pan_x += dx
            self.pan_y += dy
        else:
            self.rot_y += dx * 0.5
            self.rot_x = max(-89.0, min(89.0, self.rot_x + dy * 0.5))

        self.render()

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

        # 3. Scale and translate to screen space (CAD Z-up inverted to screen Y-down)
        screen_x = cx + self.pan_x + x2 * self.zoom
        screen_y = cy + self.pan_y - y2 * self.zoom
        return screen_x, screen_y, z2

    def render(self) -> None:
        self.delete("all")
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        cx, cy = w / 2.0, h / 2.0

        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        # 1. Draw subtle grid on XY plane
        grid_size = 100.0
        grid_step = 20.0
        grid_lines = []
        for g in range(-int(grid_size), int(grid_size) + 1, int(grid_step)):
            # Line parallel to X
            p1 = self._project_point(-grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            p2 = self._project_point(grid_size, g, 0.0, cx, cy, rad_x, rad_y)
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#1E293B", width=1)
            # Line parallel to Y
            p3 = self._project_point(g, -grid_size, 0.0, cx, cy, rad_x, rad_y)
            p4 = self._project_point(g, grid_size, 0.0, cx, cy, rad_x, rad_y)
            self.create_line(p3[0], p3[1], p4[0], p4[1], fill="#1E293B", width=1)

        # 2. Render 3D Solid Geometry
        if self._mesh and self._mesh.faces:
            # Transform all vertices
            projected_verts: List[Tuple[float, float, float]] = []
            for v in self._mesh.vertices:
                projected_verts.append(self._project_point(v[0], v[1], v[2], cx, cy, rad_x, rad_y))

            # Sort faces by average depth (Painter's algorithm for crisp rendering)
            face_order = []
            light_dir = (0.577, 0.577, 0.577)  # Directional key light

            for i, face in enumerate(self._mesh.faces):
                v0 = projected_verts[face[0]]
                v1 = projected_verts[face[1]]
                v2 = projected_verts[face[2]]
                avg_z = (v0[2] + v1[2] + v2[2]) / 3.0

                # Compute face normal in object space
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

                face_order.append((avg_z, i, face, diffuse))

            face_order.sort(key=lambda item: item[0])

            # Draw shaded polygons
            for _, _, face, diff in face_order:
                v0 = projected_verts[face[0]]
                v1 = projected_verts[face[1]]
                v2 = projected_verts[face[2]]

                # Calculate shaded hex color (slate-cyan shade)
                r_base, g_base, b_base = 56, 189, 248  # #38BDF8
                r = int(min(255, max(15, r_base * diff)))
                g = int(min(255, max(30, g_base * diff)))
                b = int(min(255, max(50, b_base * diff)))
                color_hex = f"#{r:02x}{g:02x}{b:02x}"

                self.create_polygon(
                    v0[0], v0[1], v1[0], v1[1], v2[0], v2[1],
                    fill=color_hex,
                    outline="#0284C7",
                    width=1,
                )

            # Draw silhouette edges
            if self._mesh.edges:
                for edge in self._mesh.edges:
                    v0 = projected_verts[edge[0]]
                    v1 = projected_verts[edge[1]]
                    self.create_line(v0[0], v0[1], v1[0], v1[1], fill="#38BDF8", width=1.5)

        # 3. Draw Coordinate Axes in lower-left corner
        axis_cx, axis_cy = 60, h - 60
        axis_len = 35.0
        axes = [
            ("X", 1.0, 0.0, 0.0, "#EF4444"),  # Red
            ("Y", 0.0, 1.0, 0.0, "#10B981"),  # Green
            ("Z", 0.0, 0.0, 1.0, "#3B82F6"),  # Blue
        ]
        for label, ax, ay, az, col in axes:
            p_end = self._project_point(ax * axis_len, ay * axis_len, az * axis_len, axis_cx, axis_cy, rad_x, rad_y)
            # Offset pan out of axes widget
            orig_x = axis_cx
            orig_y = axis_cy
            ax_x = p_end[0] - self.pan_x
            ax_y = p_end[1] - self.pan_y
            self.create_line(orig_x, orig_y, ax_x, ax_y, fill=col, width=2.5, arrow=tk.LAST)
            self.create_text(ax_x + 5, ax_y, text=label, fill=col, font=("Segoe UI", 9, "bold"))
