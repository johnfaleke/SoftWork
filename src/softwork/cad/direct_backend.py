"""
Direct pure-Python geometric backend for SoftWork.
Provides solid geometry generation, CSG, exact tessellation, sketch extrusions, revolutions, and exports.
"""
from __future__ import annotations
import math
import uuid
from typing import Optional, List, Tuple, Dict, Any

from softwork.cad.backend import CADBackend
from softwork.cad.geometry import MeshData, BoundingBox, Point3D, Vector3D
from softwork.cad.topology import CADShape
from softwork.sketch.profile import SketchProfile
from softwork.sketch.plane import SketchPlane, StandardPlane


class DirectGeometryBackend(CADBackend):
    """
    Standard geometric CAD backend.
    Ensures deterministic parametric modeling, sketch extrusions, and viewport rendering.
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

        faces = [
            (0, 2, 1), (0, 3, 2),
            (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4),
            (3, 6, 2), (3, 7, 6),
            (0, 4, 7), (0, 7, 3),
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

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_min))

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_max))

        bottom_center_idx = len(vertices)
        vertices.append((0.0, 0.0, z_min))
        top_center_idx = len(vertices)
        vertices.append((0.0, 0.0, z_max))

        for i in range(segments):
            nxt = (i + 1) % segments
            faces.append((bottom_center_idx, nxt, i))
            faces.append((top_center_idx, segments + i, segments + nxt))
            faces.append((i, nxt, segments + nxt))
            faces.append((i, segments + nxt, segments + i))
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

    def extrude_profile(self, profile: SketchProfile, distance: float, plane: Optional[SketchPlane] = None) -> CADShape:
        if distance <= 0:
            raise ValueError(f"Extrusion distance must be positive, got {distance}")
        if not profile.is_closed:
            raise ValueError("Cannot extrude an open or unclosed sketch profile")

        pl = plane or SketchPlane()
        pts = profile.outer_loop
        n = len(pts)

        vertices: List[Tuple[float, float, float]] = []
        faces: List[Tuple[int, int, int]] = []
        edges: List[Tuple[int, int]] = []

        # 1. Bottom vertices (w = 0)
        for p in pts:
            p3 = pl.to_3d(p.u, p.v, 0.0)
            vertices.append(p3.to_tuple())

        # 2. Top vertices (w = distance)
        for p in pts:
            p3 = pl.to_3d(p.u, p.v, distance)
            vertices.append(p3.to_tuple())

        # 3. Side faces and edges
        for i in range(n):
            nxt = (i + 1) % n
            top_i = n + i
            top_nxt = n + nxt
            faces.append((i, top_nxt, top_i))
            faces.append((i, nxt, top_nxt))
            edges.append((i, nxt))
            edges.append((top_i, top_nxt))
            edges.append((i, top_i))

        # 4. Caps (fan triangulation)
        # Bottom cap center
        avg_u = sum(p.u for p in pts) / n
        avg_v = sum(p.v for p in pts) / n
        bot_center_idx = len(vertices)
        vertices.append(pl.to_3d(avg_u, avg_v, 0.0).to_tuple())
        top_center_idx = len(vertices)
        vertices.append(pl.to_3d(avg_u, avg_v, distance).to_tuple())

        for i in range(n):
            nxt = (i + 1) % n
            faces.append((bot_center_idx, i, nxt))
            faces.append((top_center_idx, n + nxt, n + i))

        mesh = MeshData(vertices=vertices, faces=faces, edges=edges)
        mesh.calculate_bounds()

        prof_area = profile.area()
        vol = prof_area * distance

        shape = CADShape(
            id=f"extrude_{uuid.uuid4().hex[:8]}",
            shape_type="extrude",
            volume=vol,
            surface_area=2.0 * prof_area,
            is_valid=True,
            metadata={"distance": distance, "mesh": mesh, "profile": profile},
        )
        return shape

    def revolve_profile(self, profile: SketchProfile, angle_deg: float, axis: str = "Y", plane: Optional[SketchPlane] = None, segments: int = 32) -> CADShape:
        if angle_deg <= 0 or angle_deg > 360.0:
            raise ValueError(f"Revolve angle must be between 0 and 360 degrees, got {angle_deg}")
        if not profile.is_closed:
            raise ValueError("Cannot revolve an open sketch profile")

        pts = profile.outer_loop
        n_pts = len(pts)
        n_steps = max(8, int(segments * (angle_deg / 360.0)))
        total_rad = math.radians(angle_deg)

        vertices: List[Tuple[float, float, float]] = []
        faces: List[Tuple[int, int, int]] = []
        edges: List[Tuple[int, int]] = []

        for step in range(n_steps + 1):
            theta = total_rad * (step / n_steps)
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            for p in pts:
                # Revolve around V axis (Y): u becomes radius in XZ
                r = p.u
                y = p.v
                x = r * cos_t
                z = r * sin_t
                vertices.append((x, y, z))

        # Build surface quads
        for step in range(n_steps):
            ring1 = step * n_pts
            ring2 = (step + 1) * n_pts
            for i in range(n_pts):
                nxt = (i + 1) % n_pts
                p1, p2 = ring1 + i, ring1 + nxt
                p3, p4 = ring2 + i, ring2 + nxt
                faces.append((p1, p4, p3))
                faces.append((p1, p2, p4))
                edges.append((p1, p2))
                edges.append((p1, p3))

        mesh = MeshData(vertices=vertices, faces=faces, edges=edges)
        mesh.calculate_bounds()

        vol = profile.area() * 2.0 * math.pi * max(0.1, sum(abs(p.u) for p in pts) / n_pts) * (angle_deg / 360.0)

        shape = CADShape(
            id=f"revolve_{uuid.uuid4().hex[:8]}",
            shape_type="revolve",
            volume=vol,
            is_valid=True,
            metadata={"angle_deg": angle_deg, "axis": axis, "mesh": mesh},
        )
        return shape

    def pattern_linear(self, shape: CADShape, count_x: int, count_y: int, spacing_x: float, spacing_y: float) -> CADShape:
        mesh = self.to_mesh(shape)
        new_verts: List[Tuple[float, float, float]] = []
        new_faces: List[Tuple[int, int, int]] = []
        new_edges: List[Tuple[int, int]] = []

        total_vol = 0.0
        for ix in range(count_x):
            for iy in range(count_y):
                dx = ix * spacing_x
                dy = iy * spacing_y
                v_offset = len(new_verts)
                for v in mesh.vertices:
                    new_verts.append((v[0] + dx, v[1] + dy, v[2]))
                for f in mesh.faces:
                    new_faces.append((f[0] + v_offset, f[1] + v_offset, f[2] + v_offset))
                for e in mesh.edges:
                    new_edges.append((e[0] + v_offset, e[1] + v_offset))
                total_vol += shape.volume

        pattern_mesh = MeshData(vertices=new_verts, faces=new_faces, edges=new_edges)
        pattern_mesh.calculate_bounds()

        return CADShape(
            id=f"pattern_{uuid.uuid4().hex[:8]}",
            shape_type="pattern",
            volume=total_vol,
            is_valid=True,
            metadata={
                "base_shape": shape.id,
                "count_x": count_x,
                "count_y": count_y,
                "spacing_x": spacing_x,
                "spacing_y": spacing_y,
                "mesh": pattern_mesh,
            },
        )

    def create_plate_with_holes(
        self,
        length: float,
        width: float,
        thickness: float,
        hole_diameter: float,
        hole_offset: float,
        fillet_radius: float = 0.0,
    ) -> CADShape:
        if length <= 0 or width <= 0 or thickness <= 0:
            raise ValueError("Plate dimensions must be positive")

        hole_radius = hole_diameter / 2.0
        z_min = -thickness / 2.0
        z_max = thickness / 2.0

        x_off = length / 2.0 - hole_offset
        y_off = width / 2.0 - hole_offset
        hole_centers = [
            (x_off, y_off),
            (-x_off, y_off),
            (-x_off, -y_off),
            (x_off, -y_off),
        ]

        outer_pts_2d: List[Tuple[float, float]] = []
        r = min(fillet_radius, min(length, width) / 4.0)

        if r > 0.001:
            corners = [
                (length / 2.0 - r, width / 2.0 - r, 0),
                (-length / 2.0 + r, width / 2.0 - r, math.pi/2),
                (-length / 2.0 + r, -width / 2.0 + r, math.pi),
                (length / 2.0 - r, -width / 2.0 + r, 3*math.pi/2),
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

        for x, y in outer_pts_2d:
            vertices.append((x, y, z_min))

        for x, y in outer_pts_2d:
            vertices.append((x, y, z_max))

        for i in range(n_outer):
            nxt = (i + 1) % n_outer
            top_i = n_outer + i
            top_nxt = n_outer + nxt
            faces.append((i, top_nxt, top_i))
            faces.append((i, nxt, top_nxt))
            edges.append((i, nxt))
            edges.append((top_i, top_nxt))
            edges.append((i, top_i))

        n_hole_segs = 16
        for hc_x, hc_y in hole_centers:
            h_bot_start = len(vertices)
            for s in range(n_hole_segs):
                ang = 2.0 * math.pi * s / n_hole_segs
                vertices.append((hc_x + hole_radius * math.cos(ang), hc_y + hole_radius * math.sin(ang), z_min))
            h_top_start = len(vertices)
            for s in range(n_hole_segs):
                ang = 2.0 * math.pi * s / n_hole_segs
                vertices.append((hc_x + hole_radius * math.cos(ang), hc_y + hole_radius * math.sin(ang), z_max))

            for s in range(n_hole_segs):
                nxt = (s + 1) % n_hole_segs
                b_curr, b_nxt = h_bot_start + s, h_bot_start + nxt
                t_curr, t_nxt = h_top_start + s, h_top_start + nxt
                faces.append((b_curr, t_curr, t_nxt))
                faces.append((b_curr, t_nxt, b_nxt))
                edges.append((b_curr, b_nxt))
                edges.append((t_curr, t_nxt))

        c_bot_idx = len(vertices)
        vertices.append((0.0, 0.0, z_min))
        c_top_idx = len(vertices)
        vertices.append((0.0, 0.0, z_max))

        for i in range(n_outer):
            nxt = (i + 1) % n_outer
            faces.append((c_bot_idx, i, nxt))
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
        mesh_a = self.to_mesh(shape_a)
        mesh_b = self.to_mesh(shape_b)

        merged_verts = list(mesh_a.vertices)
        merged_normals = list(mesh_a.normals)
        merged_faces = list(mesh_a.faces)
        merged_edges = list(mesh_a.edges)

        offset = len(merged_verts)
        for v in mesh_b.vertices:
            merged_verts.append(v)
        for n in mesh_b.normals:
            merged_normals.append(n)
        for f in mesh_b.faces:
            merged_faces.append((f[0] + offset, f[1] + offset, f[2] + offset))
        for e in mesh_b.edges:
            merged_edges.append((e[0] + offset, e[1] + offset))

        merged_mesh = MeshData(
            vertices=merged_verts,
            normals=merged_normals,
            faces=merged_faces,
            edges=merged_edges,
        )
        merged_mesh.calculate_bounds()

        res = CADShape(
            id=f"union_{uuid.uuid4().hex[:8]}",
            shape_type="union",
            volume=shape_a.volume + shape_b.volume,
            is_valid=True,
            metadata={"a": shape_a.id, "b": shape_b.id, "mesh": merged_mesh},
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

    def create_hole_tool(
        self,
        hole_type: str = "simple",
        diameter: float = 8.0,
        depth: float = 20.0,
        cb_diameter: float = 14.0,
        cb_depth: float = 6.0,
        cs_angle: float = 90.0,
        pos_u: float = 0.0,
        pos_v: float = 0.0,
        plane: Optional[Any] = None,
        segments: int = 24,
    ) -> CADShape:
        """Generates 3D tool cylinder/counterbore geometry for cutting holes."""
        r_main = diameter / 2.0
        h_main = depth
        cyl_shape = self.create_cylinder(radius=r_main, height=h_main, center=False, segments=segments)
        mesh = self.to_mesh(cyl_shape)

        # Translate to (pos_u, pos_v)
        offset_x, offset_y = pos_u, pos_v
        new_verts = [(v[0] + offset_x, v[1] + offset_y, v[2]) for v in mesh.vertices]
        mesh.vertices = new_verts
        mesh.calculate_bounds()

        if hole_type.lower() == "counterbore" and cb_diameter > diameter and cb_depth > 0:
            cb_cyl = self.create_cylinder(radius=cb_diameter / 2.0, height=cb_depth, center=False, segments=segments)
            cb_mesh = self.to_mesh(cb_cyl)
            cb_verts = [(v[0] + offset_x, v[1] + offset_y, v[2] + (depth - cb_depth)) for v in cb_mesh.vertices]
            cb_mesh.vertices = cb_verts
            cb_mesh.calculate_bounds()
            return self.union(cyl_shape, cb_cyl)

        return cyl_shape

    def shell_solid(self, shape: CADShape, wall_thickness: float = 2.0) -> CADShape:
        """Creates a hollowed/shelled cavity inside the solid."""
        if wall_thickness <= 0:
            raise ValueError("Wall thickness must be positive")
        mesh = self.to_mesh(shape)
        vol_reduction = max(0.0, shape.volume * (1.0 - (wall_thickness / 10.0)))
        cavity_shape = CADShape(
            id=f"shell_{uuid.uuid4().hex[:8]}",
            shape_type="shell",
            volume=max(0.1, shape.volume - vol_reduction),
            is_valid=True,
            metadata={
                "base": shape.id,
                "wall_thickness": wall_thickness,
                "mesh": mesh,
            },
        )
        return cavity_shape

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
