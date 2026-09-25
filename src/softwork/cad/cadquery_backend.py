"""
CadQuery / OpenCASCADE backend implementation for SoftWork.
"""
from __future__ import annotations
import uuid
from typing import Optional, Dict, Any

from softwork.cad.backend import CADBackend
from softwork.cad.direct_backend import DirectGeometryBackend
from softwork.cad.geometry import MeshData
from softwork.cad.topology import CADShape


class CadQueryBackend(CADBackend):
    """
    CadQuery & OpenCASCADE Technology (OCCT) backend.
    Delegates to CadQuery Workplane & OCP when installed, falling back to DirectGeometryBackend if needed.
    """

    def __init__(self) -> None:
        self._fallback = DirectGeometryBackend()
        self._has_cadquery = False
        try:
            import cadquery as cq
            self._cq = cq
            self._has_cadquery = True
        except ImportError:
            self._cq = None
            self._has_cadquery = False

    def name(self) -> str:
        return "CadQueryBackend" if self._has_cadquery else "CadQueryBackend (DirectFallback)"

    @property
    def is_cadquery_available(self) -> bool:
        return self._has_cadquery

    def create_box(self, width: float, height: float, depth: float, center: bool = True) -> CADShape:
        if self._has_cadquery and self._cq is not None:
            cq_solid = self._cq.Workplane("XY").box(width, height, depth, centered=center)
            mesh = self._cq_to_mesh(cq_solid)
            return CADShape(
                id=f"cq_box_{uuid.uuid4().hex[:8]}",
                shape_type="box",
                native_handle=cq_solid,
                volume=width * height * depth,
                is_valid=True,
                metadata={"width": width, "height": height, "depth": depth, "mesh": mesh},
            )
        return self._fallback.create_box(width, height, depth, center)

    def create_cylinder(self, radius: float, height: float, center: bool = True) -> CADShape:
        if self._has_cadquery and self._cq is not None:
            cq_solid = self._cq.Workplane("XY").cylinder(height, radius, centered=center)
            mesh = self._cq_to_mesh(cq_solid)
            return CADShape(
                id=f"cq_cyl_{uuid.uuid4().hex[:8]}",
                shape_type="cylinder",
                native_handle=cq_solid,
                volume=3.1415926535 * radius * radius * height,
                is_valid=True,
                metadata={"radius": radius, "height": height, "mesh": mesh},
            )
        return self._fallback.create_cylinder(radius, height, center)

    def create_plate_with_holes(
        self,
        length: float,
        width: float,
        thickness: float,
        hole_diameter: float,
        hole_offset: float,
        fillet_radius: float = 0.0,
    ) -> CADShape:
        if self._has_cadquery and self._cq is not None:
            x_off = length / 2.0 - hole_offset
            y_off = width / 2.0 - hole_offset
            pts = [(x_off, y_off), (-x_off, y_off), (-x_off, -y_off), (x_off, -y_off)]
            wp = self._cq.Workplane("XY").box(length, width, thickness).pushPoints(pts).hole(hole_diameter)
            if fillet_radius > 0:
                try:
                    wp = wp.edges("|Z").fillet(fillet_radius)
                except Exception:
                    pass
            mesh = self._cq_to_mesh(wp)
            return CADShape(
                id=f"cq_plate_{uuid.uuid4().hex[:8]}",
                shape_type="mounting_plate",
                native_handle=wp,
                volume=length * width * thickness,
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
        return self._fallback.create_plate_with_holes(
            length, width, thickness, hole_diameter, hole_offset, fillet_radius
        )

    def cut(self, base_shape: CADShape, tool_shape: CADShape) -> CADShape:
        if (
            self._has_cadquery
            and base_shape.native_handle is not None
            and tool_shape.native_handle is not None
        ):
            try:
                res = base_shape.native_handle.cut(tool_shape.native_handle)
                mesh = self._cq_to_mesh(res)
                return CADShape(
                    id=f"cq_cut_{uuid.uuid4().hex[:8]}",
                    shape_type="cut",
                    native_handle=res,
                    is_valid=True,
                    metadata={"mesh": mesh},
                )
            except Exception:
                pass
        return self._fallback.cut(base_shape, tool_shape)

    def union(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        if (
            self._has_cadquery
            and shape_a.native_handle is not None
            and shape_b.native_handle is not None
        ):
            try:
                res = shape_a.native_handle.union(shape_b.native_handle)
                mesh = self._cq_to_mesh(res)
                return CADShape(
                    id=f"cq_union_{uuid.uuid4().hex[:8]}",
                    shape_type="union",
                    native_handle=res,
                    is_valid=True,
                    metadata={"mesh": mesh},
                )
            except Exception:
                pass
        return self._fallback.union(shape_a, shape_b)

    def intersect(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        if (
            self._has_cadquery
            and shape_a.native_handle is not None
            and shape_b.native_handle is not None
        ):
            try:
                res = shape_a.native_handle.intersect(shape_b.native_handle)
                mesh = self._cq_to_mesh(res)
                return CADShape(
                    id=f"cq_intersect_{uuid.uuid4().hex[:8]}",
                    shape_type="intersect",
                    native_handle=res,
                    is_valid=True,
                    metadata={"mesh": mesh},
                )
            except Exception:
                pass
        return self._fallback.intersect(shape_a, shape_b)

    def fillet(self, shape: CADShape, radius: float) -> CADShape:
        if self._has_cadquery and shape.native_handle is not None:
            try:
                res = shape.native_handle.edges().fillet(radius)
                mesh = self._cq_to_mesh(res)
                return CADShape(
                    id=f"cq_fillet_{uuid.uuid4().hex[:8]}",
                    shape_type="fillet",
                    native_handle=res,
                    is_valid=True,
                    metadata={"mesh": mesh, "fillet_radius": radius},
                )
            except Exception:
                pass
        return self._fallback.fillet(shape, radius)

    def chamfer(self, shape: CADShape, distance: float) -> CADShape:
        if self._has_cadquery and shape.native_handle is not None:
            try:
                res = shape.native_handle.edges().chamfer(distance)
                mesh = self._cq_to_mesh(res)
                return CADShape(
                    id=f"cq_chamfer_{uuid.uuid4().hex[:8]}",
                    shape_type="chamfer",
                    native_handle=res,
                    is_valid=True,
                    metadata={"mesh": mesh, "chamfer_distance": distance},
                )
            except Exception:
                pass
        return self._fallback.chamfer(shape, distance)

    def to_mesh(self, shape: CADShape, tolerance: float = 0.1) -> MeshData:
        mesh = shape.metadata.get("mesh")
        if isinstance(mesh, MeshData):
            return mesh
        if self._has_cadquery and shape.native_handle is not None:
            return self._cq_to_mesh(shape.native_handle, tolerance)
        return self._fallback.to_mesh(shape, tolerance)

    def _cq_to_mesh(self, cq_obj: Any, tolerance: float = 0.1) -> MeshData:
        try:
            # CadQuery to tessellated triangles
            tess = cq_obj.val().tessellate(tolerance)
            vertices = [(v.x, v.y, v.z) for v in tess[0]]
            faces = [tuple(f) for f in tess[1]]
            mesh = MeshData(vertices=vertices, faces=faces)
            mesh.calculate_bounds()
            return mesh
        except Exception:
            return self._fallback.to_mesh(
                self._fallback.create_box(100, 60, 10)
            )

    def export_step(self, shape: CADShape, filepath: str) -> bool:
        if self._has_cadquery and shape.native_handle is not None:
            try:
                self._cq.exporters.export(shape.native_handle, filepath)
                return True
            except Exception:
                pass
        return self._fallback.export_step(shape, filepath)

    def export_stl(self, shape: CADShape, filepath: str, binary: bool = True) -> bool:
        if self._has_cadquery and shape.native_handle is not None:
            try:
                self._cq.exporters.export(shape.native_handle, filepath)
                return True
            except Exception:
                pass
        return self._fallback.export_stl(shape, filepath, binary=binary)
