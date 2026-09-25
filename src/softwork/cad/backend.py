"""
Abstract CAD backend interface for SoftWork.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any

from softwork.cad.geometry import MeshData
from softwork.cad.topology import CADShape


class CADBackend(ABC):
    """
    Abstract interface for geometric kernel operations.
    Decouples document/feature logic from underlying CAD libraries (CadQuery, OpenCASCADE, Direct OCCT).
    """

    @abstractmethod
    def name(self) -> str:
        """Name of the backend implementation."""
        pass

    @abstractmethod
    def create_box(self, width: float, height: float, depth: float, center: bool = True) -> CADShape:
        """Create a 3D box solid."""
        pass

    @abstractmethod
    def create_cylinder(self, radius: float, height: float, center: bool = True) -> CADShape:
        """Create a 3D cylinder solid."""
        pass

    @abstractmethod
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
        Create a parametric mounting plate with four corner holes and optional outer fillet.
        """
        pass

    @abstractmethod
    def cut(self, base_shape: CADShape, tool_shape: CADShape) -> CADShape:
        """Perform boolean difference: base_shape - tool_shape."""
        pass

    @abstractmethod
    def union(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        """Perform boolean union: shape_a + shape_b."""
        pass

    @abstractmethod
    def intersect(self, shape_a: CADShape, shape_b: CADShape) -> CADShape:
        """Perform boolean intersection: shape_a ∩ shape_b."""
        pass

    @abstractmethod
    def fillet(self, shape: CADShape, radius: float) -> CADShape:
        """Apply fillet with given radius to outer edges."""
        pass

    @abstractmethod
    def chamfer(self, shape: CADShape, distance: float) -> CADShape:
        """Apply chamfer with given distance to outer edges."""
        pass

    @abstractmethod
    def to_mesh(self, shape: CADShape, tolerance: float = 0.1) -> MeshData:
        """Tessellate CAD shape to renderable MeshData."""
        pass

    @abstractmethod
    def export_step(self, shape: CADShape, filepath: str) -> bool:
        """Export solid geometry to ISO-10303 STEP format."""
        pass

    @abstractmethod
    def export_stl(self, shape: CADShape, filepath: str, binary: bool = True) -> bool:
        """Export solid geometry to STL format."""
        pass
