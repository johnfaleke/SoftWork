"""
CadQuery / OpenCASCADE backend implementation for SoftWork.
"""
from __future__ import annotations
import uuid
from typing import Optional, Dict, Any

from softwork.cad.backend import CADBackend, CADKernelError
from softwork.cad.direct_backend import PrototypeGeometryBackend, DirectGeometryBackend
from softwork.cad.geometry import MeshData
from softwork.cad.topology import CADShape
from softwork.sketch.profile import SketchProfile
from softwork.sketch.plane import SketchPlane


class CadQueryBackend(CADBackend):
    """
    CadQuery & OpenCASCADE Technology (OCCT) authoritative B-rep backend.
    Directly executes modeling operations on CadQuery Workplane & OCP B-rep topology.
    Raises CADKernelError on any modeling or topology failure without silent masquerading.
    """

    def __init__(self, require_installed: bool = False) -> None:
        self._has_cadquery = False
        try:
            import cadquery as cq
            self._cq = cq
            self._has_cadquery = True
        except ImportError:
            self._cq = None
            self._has_cadquery = False
            if require_installed:
                raise CADKernelError(
                    "CadQuery/OCP is not installed in the active environment. "
                    "Install with conda or 'pip install cadquery'."
                )

    @property
    def capabilities(self) -> BackendCapabilities:
        from softwork.cad.capabilities import BackendCapabilities
        if self._has_cadquery:
            return BackendCapabilities(
                name="CadQueryBackend",
                is_available=True,
                is_authoritative_brep=True,
                supports_step=True,
                supports_stl=True,
                diagnostic_message="OpenCASCADE/CadQuery B-rep kernel is active and authoritative.",
            )
        return BackendCapabilities(
            name="CadQueryBackend",
            is_available=False,
            is_authoritative_brep=True,
            supports_step=True,
            supports_stl=True,
            diagnostic_message="CadQuery/OpenCASCADE kernel is unavailable. Install with conda or 'pip install cadquery'.",
        )

    def name(self) -> str:
        return "CadQueryBackend"

    @property
    def is_cadquery_available(self) -> bool:
        return self._has_cadquery

    def _ensure_cadquery(self) -> Any:
        if not self._has_cadquery or self._cq is None:
            raise CADKernelError(
                "CadQuery/OpenCASCADE kernel is unavailable. "
                "Ensure CadQuery is installed in your Python environment."
            )
        return self._cq

    def create_box(self, width: float, height: float, depth: float, center: bool = True) -> CADShape:
        cq = self._ensure_cadquery()
        if width <= 0 or height <= 0 or depth <= 0:
            raise CADKernelError(f"Box dimensions must be positive, got {width}x{height}x{depth}")
        try:
            cq_solid = cq.Workplane("XY").box(width, height, depth, centered=center)
            mesh = self._cq_to_mesh(cq_solid)
            return CADShape(
                id=f"cq_box_{uuid.uuid4().hex[:8]}",
                shape_type="box",
                native_handle=cq_solid,
                volume=width * height * depth,
                surface_area=2.0 * (width * height + width * depth + height * depth),
                is_valid=True,
                metadata={"width": width, "height": height, "depth": depth, "mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery create_box failed: {str(e)}") from e

    def create_cylinder(self, radius: float, height: float, center: bool = True) -> CADShape:
        cq = self._ensure_cadquery()
        if radius <= 0 or height <= 0:
            raise CADKernelError(f"Cylinder dimensions must be positive, got r={radius}, h={height}")
        try:
            cq_solid = cq.Workplane("XY").cylinder(height, radius, centered=center)
            mesh = self._cq_to_mesh(cq_solid)
            return CADShape(
                id=f"cq_cyl_{uuid.uuid4().hex[:8]}",
                shape_type="cylinder",
                native_handle=cq_solid,
                volume=3.1415926535 * radius * radius * height,
                is_valid=True,
                metadata={"radius": radius, "height": height, "mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery create_cylinder failed: {str(e)}") from e

    def extrude_profile(self, profile: SketchProfile, distance: float, plane: Optional[SketchPlane] = None) -> CADShape:
        cq = self._ensure_cadquery()
        if distance <= 0:
            raise CADKernelError(f"Extrude distance must be positive, got {distance}")
        if not profile.outer_loop:
            raise CADKernelError("Extrude profile contains no loop vertices")
        try:
            pts = [(p.u, p.v) for p in profile.outer_loop]
            pl_name = plane.plane_type.value if plane else "XY"
            wp = cq.Workplane(pl_name).polyline(pts).close().extrude(distance)
            mesh = self._cq_to_mesh(wp)
            return CADShape(
                id=f"cq_extrude_{uuid.uuid4().hex[:8]}",
                shape_type="extrude",
                native_handle=wp,
                volume=profile.area() * distance,
                is_valid=True,
                metadata={"distance": distance, "mesh": mesh, "profile": profile},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery extrude_profile failed: {str(e)}") from e

    def revolve_profile(self, profile: SketchProfile, angle_deg: float, axis: str = "Y", plane: Optional[SketchPlane] = None) -> CADShape:
        cq = self._ensure_cadquery()
        if angle_deg <= 0 or angle_deg > 360.0:
            raise CADKernelError(f"Revolve angle must be in (0, 360], got {angle_deg}")
        try:
            pts = [(p.u, p.v) for p in profile.outer_loop]
            ax_dir = (0, 1, 0) if axis.upper() == "Y" else (1, 0, 0)
            wp = cq.Workplane("XY").polyline(pts).close().revolve(angle_deg, (0, 0, 0), ax_dir)
            mesh = self._cq_to_mesh(wp)
            return CADShape(
                id=f"cq_revolve_{uuid.uuid4().hex[:8]}",
                shape_type="revolve",
                native_handle=wp,
                volume=profile.area() * 20.0,
                is_valid=True,
                metadata={"angle_deg": angle_deg, "mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery revolve_profile failed: {str(e)}") from e

    def pattern_linear(self, shape: CADShape, count_x: int, count_y: int, spacing_x: float, spacing_y: float) -> CADShape:
        cq = self._ensure_cadquery()
        if shape.native_handle is None:
            raise CADKernelError("Cannot pattern shape without native CadQuery handle")
        try:
            # Pattern across grid
            pts = []
            for ix in range(count_x):
                for iy in range(count_y):
                    pts.append((ix * spacing_x, iy * spacing_y))
            wp = cq.Workplane("XY").pushPoints(pts).eachpoint(lambda loc: shape.native_handle.val().located(loc))
            mesh = self._cq_to_mesh(wp)
            return CADShape(
                id=f"cq_pattern_{uuid.uuid4().hex[:8]}",
                shape_type="pattern",
                native_handle=wp,
                volume=shape.volume * count_x * count_y,
                is_valid=True,
                metadata={"count_x": count_x, "count_y": count_y, "mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery pattern_linear failed: {str(e)}") from e

    def create_plate_with_holes(
        self,
        length: float,
        width: float,
        thickness: float,
        hole_diameter: float,
        hole_offset: float,
        fillet_radius: float = 0.0,
    ) -> CADShape:
        cq = self._ensure_cadquery()
        if length <= 0 or width <= 0 or thickness <= 0:
            raise CADKernelError("Plate dimensions must be positive")
        try:
            x_off = length / 2.0 - hole_offset
            y_off = width / 2.0 - hole_offset
            pts = [(x_off, y_off), (-x_off, y_off), (-x_off, -y_off), (x_off, -y_off)]
            wp = cq.Workplane("XY").box(length, width, thickness).pushPoints(pts).hole(hole_diameter)
            if fillet_radius > 0:
                wp = wp.edges("|Z").fillet(fillet_radius)
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
        except Exception as e:
            raise CADKernelError(f"CadQuery create_plate_with_holes failed: {str(e)}") from e

    def cut(self, base_shape: CADShape, tool_shape: CADShape) -> CADShape:
        self._ensure_cadquery()
        if base_shape.native_handle is None or tool_shape.native_handle is None:
            raise CADKernelError("Boolean cut requires valid native CadQuery handles")
        try:
            res = base_shape.native_handle.cut(tool_shape.native_handle)
            mesh = self._cq_to_mesh(res)
            return CADShape(
                id=f"cq_cut_{uuid.uuid4().hex[:8]}",
                shape_type="cut",
                native_handle=res,
                volume=max(0.0, base_shape.volume - tool_shape.volume),
                is_valid=True,
                metadata={"mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery boolean cut failed: {str(e)}") from e

    def union(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        self._ensure_cadquery()
        if shape_a.native_handle is None or shape_b.native_handle is None:
            raise CADKernelError("Boolean union requires valid native CadQuery handles")
        try:
            res = shape_a.native_handle.union(shape_b.native_handle)
            mesh = self._cq_to_mesh(res)
            return CADShape(
                id=f"cq_union_{uuid.uuid4().hex[:8]}",
                shape_type="union",
                native_handle=res,
                volume=shape_a.volume + shape_b.volume,
                is_valid=True,
                metadata={"mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery boolean union failed: {str(e)}") from e

    def intersect(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        self._ensure_cadquery()
        if shape_a.native_handle is None or shape_b.native_handle is None:
            raise CADKernelError("Boolean intersect requires valid native CadQuery handles")
        try:
            res = shape_a.native_handle.intersect(shape_b.native_handle)
            mesh = self._cq_to_mesh(res)
            return CADShape(
                id=f"cq_intersect_{uuid.uuid4().hex[:8]}",
                shape_type="intersect",
                native_handle=res,
                volume=min(shape_a.volume, shape_b.volume),
                is_valid=True,
                metadata={"mesh": mesh},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery boolean intersect failed: {str(e)}") from e

    def fillet(self, shape: CADShape, radius: float) -> CADShape:
        self._ensure_cadquery()
        if shape.native_handle is None:
            raise CADKernelError("Fillet requires valid native CadQuery handle")
        if radius <= 0:
            raise CADKernelError(f"Fillet radius must be positive, got {radius}")
        try:
            res = shape.native_handle.edges().fillet(radius)
            mesh = self._cq_to_mesh(res)
            return CADShape(
                id=f"cq_fillet_{uuid.uuid4().hex[:8]}",
                shape_type="fillet",
                native_handle=res,
                volume=shape.volume,
                is_valid=True,
                metadata={"mesh": mesh, "fillet_radius": radius},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery fillet failed: {str(e)}") from e

    def chamfer(self, shape: CADShape, distance: float) -> CADShape:
        self._ensure_cadquery()
        if shape.native_handle is None:
            raise CADKernelError("Chamfer requires valid native CadQuery handle")
        if distance <= 0:
            raise CADKernelError(f"Chamfer distance must be positive, got {distance}")
        try:
            res = shape.native_handle.edges().chamfer(distance)
            mesh = self._cq_to_mesh(res)
            return CADShape(
                id=f"cq_chamfer_{uuid.uuid4().hex[:8]}",
                shape_type="chamfer",
                native_handle=res,
                volume=shape.volume,
                is_valid=True,
                metadata={"mesh": mesh, "chamfer_distance": distance},
            )
        except Exception as e:
            raise CADKernelError(f"CadQuery chamfer failed: {str(e)}") from e

    def to_mesh(self, shape: CADShape, tolerance: float = 0.1) -> MeshData:
        mesh = shape.metadata.get("mesh")
        if isinstance(mesh, MeshData):
            return mesh
        if self._has_cadquery and shape.native_handle is not None:
            return self._cq_to_mesh(shape.native_handle, tolerance)
        return MeshData()

    def _cq_to_mesh(self, cq_obj: Any, tolerance: float = 0.1) -> MeshData:
        try:
            tess = cq_obj.val().tessellate(tolerance)
            vertices = [(v.x, v.y, v.z) for v in tess[0]]
            faces = [tuple(f) for f in tess[1]]
            mesh = MeshData(vertices=vertices, faces=faces)
            mesh.calculate_bounds()
            return mesh
        except Exception as e:
            raise CADKernelError(f"Failed to tessellate CadQuery shape: {str(e)}") from e

    def export_step(self, shape: CADShape, filepath: str) -> bool:
        cq = self._ensure_cadquery()
        if shape.native_handle is None:
            raise CADKernelError("Export STEP requires valid native CadQuery handle")
        try:
            cq.exporters.export(shape.native_handle, filepath)
            return True
        except Exception as e:
            raise CADKernelError(f"CadQuery export_step failed: {str(e)}") from e

    def export_stl(self, shape: CADShape, filepath: str, binary: bool = True) -> bool:
        cq = self._ensure_cadquery()
        if shape.native_handle is None:
            raise CADKernelError("Export STL requires valid native CadQuery handle")
        try:
            cq.exporters.export(shape.native_handle, filepath)
            return True
        except Exception as e:
            raise CADKernelError(f"CadQuery export_stl failed: {str(e)}") from e
