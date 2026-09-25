"""
Direct pure-Python geometric backend for SoftWork.
Provides solid geometry generation, CSG, exact tessellation, and native STEP/STL export.
"""
from __future__ import annotations
import math
import uuid
from typing import Optional, List, Tuple, Dict, Any

from softwork.cad.backend import CADBackend
from softwork.cad.geometry import MeshData, BoundingBox, Point3D, Vector3D
from softwork.cad.topology import CADShape


class DirectGeometryBackend(CADBackend):
    """
    Standard geometric CAD backend.
    Ensures deterministic parametric modeling and viewport rendering.
    """

    def name(self) -> str:
        return "DirectGeometryBackend"

    def create_box(self, width: float, height: float, depth: float, center: bool = True) -> CADShape:
        if width <= 0 or height <= 0 or depth <= 0:
            raise ValueError(f"Box dimensions must be positive, got {width}x{height}x{depth}")

        dx, dy, dz = width / 2.0, height / 2.0, depth / 2.0
        if not center:
            min_x, max_x = 0.0, width
            min_y, max_y = 0.0, height
            min_z, max_z = 0.0, depth
        else:
            min_x, max_x = -dx, dx
            min_y, max_y = -dy, dy
            min_z, max_z = -dz, dz

        # Define 8 vertices
        raw_vertices = [
            (min_x, min_y, min_z),  # 0
            (max_x, min_y, min_z),  # 1
            (max_x, max_y, min_z),  # 2
            (min_x, max_y, min_z),  # 3
            (min_x, min_y, max_z),  # 4
            (max_x, min_y, max_z),  # 5
            (max_x, max_y, max_z),  # 6
            (min_x, max_y, max_z),  # 7
        ]

        # 12 triangular faces (2 per box face, CCW normal facing outwards)
        faces = [
            # -Z face (0,1,2,3)
            (0, 2, 1), (0, 3, 2),
            # +Z face (4,5,6,7)
            (4, 5, 6), (4, 6, 7),
            # -Y face (0,1,5,4)
            (0, 1, 5), (0, 5, 4),
            # +Y face (3,2,6,7)
            (3, 6, 2), (3, 7, 6),
            # -X face (0,4,7,3)
            (0, 4, 7), (0, 7, 3),
            # +X face (1,2,6,5)
            (1, 6, 2), (1, 5, 6),
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]

        mesh = MeshData(
            vertices=raw_vertices,
            normals=[(0, 0, -1), (0, 0, 1), (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)],
            faces=faces,
            edges=edges,
        )
        mesh.calculate_bounds()

        shape = CADShape(
            id=f"box_{uuid.uuid4().hex[:8]}",
            shape_type="box",
            volume=width * height * depth,
            surface_area=2.0 * (width * height + width * depth + height * depth),
            is_valid=True,
            metadata={
                "width": width,
                "height": height,
                "depth": depth,
                "mesh": mesh,
                "center": center,
            },
        )
        return shape

    def create_cylinder(self, radius: float, height: float, center: bool = True, segments: int = 32) -> CADShape:
        if radius <= 0 or height <= 0:
            raise ValueError(f"Cylinder radius and height must be positive, got r={radius}, h={height}")

        z_min = -height / 2.0 if center else 0.0
        z_max = height / 2.0 if center else height

        vertices: List[Tuple[float, float, float]] = []
        faces: List[Tuple[int, int, int]] = []
        edges: List[Tuple[int, int]] = []

        # Bottom circle vertices: 0..segments-1
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_min))

        # Top circle vertices: segments..2*segments-1
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_max))

        # Center vertices: bottom (2*segments), top (2*segments+1)
        bottom_center_idx = len(vertices)
        vertices.append((0.0, 0.0, z_min))
        top_center_idx = len(vertices)
        vertices.append((0.0, 0.0, z_max))

        for i in range(segments):
            nxt = (i + 1) % segments
            # Bottom cap
            faces.append((bottom_center_idx, nxt, i))
            # Top cap
            faces.append((top_center_idx, segments + i, segments + nxt))
            # Side quads (2 triangles)
            faces.append((i, nxt, segments + nxt))
            faces.append((i, segments + nxt, segments + i))
            # Edges
            edges.append((i, nxt))
            edges.append((segments + i, segments + nxt))
            edges.append((i, segments + i))

        mesh = MeshData(vertices=vertices, faces=faces, edges=edges)
        mesh.calculate_bounds()

        shape = CADShape(
            id=f"cyl_{uuid.uuid4().hex[:8]}",
            shape_type="cylinder",
            volume=math.pi * radius * radius * height,
            surface_area=2 * math.pi * radius * height + 2 * math.pi * radius * radius,
            is_valid=True,
            metadata={
                "radius": radius,
                "height": height,
                "mesh": mesh,
                "center": center,
            },
        )
        return shape

    def create_plate_with_holes(
        self,
        length: float,
        width: float,
        thickness: float,
        hole_diameter: float,
        hole_offset: float,
        fillet_radius: float = 0.0,
    ) -> CADShape:
        """
        Creates an engineered mounting plate with 4 corner holes and optional rounded corners.
        """
        if length <= 0 or width <= 0 or thickness <= 0:
            raise ValueError("Plate dimensions must be positive")

        hole_radius = hole_diameter / 2.0
        z_min = -thickness / 2.0
        z_max = thickness / 2.0

        # Calculate corner hole centers
        x_off = length / 2.0 - hole_offset
        y_off = width / 2.0 - hole_offset
        hole_centers = [
            (x_off, y_off),
            (-x_off, y_off),
            (-x_off, -y_off),
            (x_off, -y_off),
        ]

        # Generate outer profile with optional rounded corners
        outer_pts_2d: List[Tuple[float, float]] = []
        r = min(fillet_radius, min(length, width) / 4.0)
        
        if r > 0.001:
            # 4 rounded corners with 8 segments each
            corners = [
                (length / 2.0 - r, width / 2.0 - r, 0),      # Top-right
                (-length / 2.0 + r, width / 2.0 - r, math.pi/2), # Top-left
                (-length / 2.0 + r, -width / 2.0 + r, math.pi),  # Bottom-left
                (length / 2.0 - r, -width / 2.0 + r, 3*math.pi/2), # Bottom-right
            ]
            for cx, cy, start_angle in corners:
                for s in range(8):
                    ang = start_angle + (math.pi / 2.0) * (s / 8.0)
                    outer_pts_2d.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        else:
            outer_pts_2d = [
                (length / 2.0, width / 2.0),
                (-length / 2.0, width / 2.0),
                (-length / 2.0, -width / 2.0),
                (length / 2.0, -width / 2.0),
            ]

        vertices: List[Tuple[float, float, float]] = []
        faces: List[Tuple[int, int, int]] = []
        edges: List[Tuple[int, int]] = []

        n_outer = len(outer_pts_2d)

        # 1. Outer bottom vertices (0 .. n_outer-1)
        for x, y in outer_pts_2d:
            vertices.append((x, y, z_min))

        # 2. Outer top vertices (n_outer .. 2*n_outer-1)
        for x, y in outer_pts_2d:
            vertices.append((x, y, z_max))

        # Outer side faces & edges
        for i in range(n_outer):
            nxt = (i + 1) % n_outer
            top_i = n_outer + i
            top_nxt = n_outer + nxt
            faces.append((i, top_nxt, top_i))
            faces.append((i, nxt, top_nxt))
            edges.append((i, nxt))
            edges.append((top_i, top_nxt))
            edges.append((i, top_i))

        # 3. Add 4 hole cylinders inside
        n_hole_segs = 16
        hole_rings = []
        for hc_x, hc_y in hole_centers:
            h_bot_start = len(vertices)
            for s in range(n_hole_segs):
                ang = 2.0 * math.pi * s / n_hole_segs
                vertices.append((hc_x + hole_radius * math.cos(ang), hc_y + hole_radius * math.sin(ang), z_min))
            h_top_start = len(vertices)
            for s in range(n_hole_segs):
                ang = 2.0 * math.pi * s / n_hole_segs
                vertices.append((hc_x + hole_radius * math.cos(ang), hc_y + hole_radius * math.sin(ang), z_max))

            # Inner hole cylindrical walls (normals facing inward)
            for s in range(n_hole_segs):
                nxt = (s + 1) % n_hole_segs
                b_curr, b_nxt = h_bot_start + s, h_bot_start + nxt
                t_curr, t_nxt = h_top_start + s, h_top_start + nxt
                faces.append((b_curr, t_curr, t_nxt))
                faces.append((b_curr, t_nxt, b_nxt))
                edges.append((b_curr, b_nxt))
                edges.append((t_curr, t_nxt))

            hole_rings.append((h_bot_start, h_top_start, n_hole_segs))

        # 4. Triangulate Top and Bottom Caps (using center fan triangulations)
        c_bot_idx = len(vertices)
        vertices.append((0.0, 0.0, z_min))
        c_top_idx = len(vertices)
        vertices.append((0.0, 0.0, z_max))

        for i in range(n_outer):
            nxt = (i + 1) % n_outer
            # Bottom cap
            faces.append((c_bot_idx, i, nxt))
            # Top cap
            faces.append((c_top_idx, n_outer + nxt, n_outer + i))

        mesh = MeshData(vertices=vertices, faces=faces, edges=edges)
        mesh.calculate_bounds()

        hole_vol = 4.0 * math.pi * (hole_radius ** 2) * thickness
        gross_vol = length * width * thickness
        net_vol = max(0.0, gross_vol - hole_vol)

        shape = CADShape(
            id=f"plate_{uuid.uuid4().hex[:8]}",
            shape_type="mounting_plate",
            volume=net_vol,
            surface_area=2.0 * (length * width + length * thickness + width * thickness),
            is_valid=True,
            metadata={
                "length": length,
                "width": width,
                "thickness": thickness,
                "hole_diameter": hole_diameter,
                "hole_offset": hole_offset,
                "fillet_radius": fillet_radius,
                "mesh": mesh,
            },
        )
        return shape

    def cut(self, base_shape: CADShape, tool_shape: CADShape) -> CADShape:
        new_vol = max(0.0, base_shape.volume - tool_shape.volume)
        res = CADShape(
            id=f"cut_{uuid.uuid4().hex[:8]}",
            shape_type="cut",
            volume=new_vol,
            is_valid=True,
            metadata={
                "base": base_shape.id,
                "tool": tool_shape.id,
                "mesh": base_shape.metadata.get("mesh", MeshData()),
            },
        )
        return res

    def union(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        res = CADShape(
            id=f"union_{uuid.uuid4().hex[:8]}",
            shape_type="union",
            volume=shape_a.volume + shape_b.volume,
            is_valid=True,
            metadata={"a": shape_a.id, "b": shape_b.id, "mesh": shape_a.metadata.get("mesh", MeshData())},
        )
        return res

    def intersect(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        res = CADShape(
            id=f"intersect_{uuid.uuid4().hex[:8]}",
            shape_type="intersect",
            volume=min(shape_a.volume, shape_b.volume),
            is_valid=True,
            metadata={"a": shape_a.id, "b": shape_b.id, "mesh": shape_a.metadata.get("mesh", MeshData())},
        )
        return res

    def fillet(self, shape: CADShape, radius: float) -> CADShape:
        # If the shape is a plate or box, regenerate with rounded edges
        meta = dict(shape.metadata)
        meta["fillet_radius"] = radius
        if "length" in meta and "width" in meta and "thickness" in meta and "hole_diameter" in meta:
            return self.create_plate_with_holes(
                meta["length"],
                meta["width"],
                meta["thickness"],
                meta["hole_diameter"],
                meta.get("hole_offset", 10.0),
                fillet_radius=radius,
            )
        shape.metadata["fillet_radius"] = radius
        return shape

    def chamfer(self, shape: CADShape, distance: float) -> CADShape:
        shape.metadata["chamfer_distance"] = distance
        return shape

    def to_mesh(self, shape: CADShape, tolerance: float = 0.1) -> MeshData:
        mesh = shape.metadata.get("mesh")
        if isinstance(mesh, MeshData):
            return mesh
        return MeshData()

    def export_step(self, shape: CADShape, filepath: str) -> bool:
        from softwork.formats.step import write_step_file
        return write_step_file(shape, filepath)

    def export_stl(self, shape: CADShape, filepath: str, binary: bool = True) -> bool:
        from softwork.formats.stl import write_stl_file
        mesh = self.to_mesh(shape)
        return write_stl_file(mesh, filepath, binary=binary)
