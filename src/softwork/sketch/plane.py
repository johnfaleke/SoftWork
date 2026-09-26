"""
Datum planes and coordinate transforms for 2D sketching.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from softwork.cad.geometry import Point3D, Vector3D


class StandardPlane(str, Enum):
    XY = "XY"
    XZ = "XZ"
    YZ = "YZ"


@dataclass
class SketchPlane:
    """
    3D Plane in space where 2D sketch elements reside.
    Defined by an origin point, u-axis (X in 2D), v-axis (Y in 2D), and normal (Z in 2D).
    """
    plane_type: StandardPlane = StandardPlane.XY
    origin: Point3D = field(default_factory=lambda: Point3D(0.0, 0.0, 0.0))
    u_axis: Vector3D = field(default_factory=lambda: Vector3D(1.0, 0.0, 0.0))
    v_axis: Vector3D = field(default_factory=lambda: Vector3D(0.0, 1.0, 0.0))
    normal: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 1.0))

    @classmethod
    def from_standard(cls, plane_type: StandardPlane, offset: float = 0.0) -> SketchPlane:
        if plane_type == StandardPlane.XY:
            return cls(
                plane_type=StandardPlane.XY,
                origin=Point3D(0.0, 0.0, offset),
                u_axis=Vector3D(1.0, 0.0, 0.0),
                v_axis=Vector3D(0.0, 1.0, 0.0),
                normal=Vector3D(0.0, 0.0, 1.0),
            )
        elif plane_type == StandardPlane.XZ:
            return cls(
                plane_type=StandardPlane.XZ,
                origin=Point3D(0.0, offset, 0.0),
                u_axis=Vector3D(1.0, 0.0, 0.0),
                v_axis=Vector3D(0.0, 0.0, 1.0),
                normal=Vector3D(0.0, -1.0, 0.0),
            )
        elif plane_type == StandardPlane.YZ:
            return cls(
                plane_type=StandardPlane.YZ,
                origin=Point3D(offset, 0.0, 0.0),
                u_axis=Vector3D(0.0, 1.0, 0.0),
                v_axis=Vector3D(0.0, 0.0, 1.0),
                normal=Vector3D(1.0, 0.0, 0.0),
            )
        return cls()

    def to_3d(self, u: float, v: float, w: float = 0.0) -> Point3D:
        """Transforms 2D (u, v) sketch coordinate into 3D world space coordinate."""
        x = self.origin.x + u * self.u_axis.x + v * self.v_axis.x + w * self.normal.x
        y = self.origin.y + u * self.u_axis.y + v * self.v_axis.y + w * self.normal.y
        z = self.origin.z + u * self.u_axis.z + v * self.v_axis.z + w * self.normal.z
        return Point3D(x, y, z)
