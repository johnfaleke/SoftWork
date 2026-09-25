"""
CAD backend and geometry subsystem.
"""
from softwork.cad.geometry import Point3D, Vector3D, BoundingBox, MeshData
from softwork.cad.topology import CADShape, TopologyEntity, TopologyType
from softwork.cad.backend import CADBackend
from softwork.cad.direct_backend import DirectGeometryBackend
from softwork.cad.cadquery_backend import CadQueryBackend
from softwork.cad.validation import GeometryValidator, ValidationReport, ValidationIssue

__all__ = [
    "Point3D",
    "Vector3D",
    "BoundingBox",
    "MeshData",
    "CADShape",
    "TopologyEntity",
    "TopologyType",
    "CADBackend",
    "DirectGeometryBackend",
    "CadQueryBackend",
    "GeometryValidator",
    "ValidationReport",
    "ValidationIssue",
]
