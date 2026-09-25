"""
Geometric primitives and mesh data structures.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float

    def distance_to(self, other: Point3D) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True)
class Vector3D:
    x: float
    y: float
    z: float

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self) -> Vector3D:
        l = self.length()
        if l == 0.0:
            return Vector3D(0.0, 0.0, 1.0)
        return Vector3D(self.x / l, self.y / l, self.z / l)

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D) -> Vector3D:
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


@dataclass
class BoundingBox:
    min_x: float = 0.0
    min_y: float = 0.0
    min_z: float = 0.0
    max_x: float = 0.0
    max_y: float = 0.0
    max_z: float = 0.0

    @property
    def width(self) -> float:
        return max(0.0, self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return max(0.0, self.max_y - self.min_y)

    @property
    def depth(self) -> float:
        return max(0.0, self.max_z - self.min_z)

    @property
    def center(self) -> Point3D:
        return Point3D(
            (self.min_x + self.max_x) / 2.0,
            (self.min_y + self.max_y) / 2.0,
            (self.min_z + self.max_z) / 2.0,
        )

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

    def expand_to_include(self, p: Point3D) -> None:
        self.min_x = min(self.min_x, p.x)
        self.min_y = min(self.min_y, p.y)
        self.min_z = min(self.min_z, p.z)
        self.max_x = max(self.max_x, p.x)
        self.max_y = max(self.max_y, p.y)
        self.max_z = max(self.max_z, p.z)


@dataclass
class MeshData:
    """Triangulated mesh data suitable for 3D rendering and STL/OBJ export."""
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)
    faces: List[Tuple[int, int, int]] = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)
    bounds: BoundingBox = field(default_factory=BoundingBox)

    def calculate_bounds(self) -> BoundingBox:
        if not self.vertices:
            self.bounds = BoundingBox()
            return self.bounds
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        self.bounds = BoundingBox(
            min_x=min(xs),
            min_y=min(ys),
            min_z=min(zs),
            max_x=max(xs),
            max_y=max(ys),
            max_z=max(zs),
        )
        return self.bounds
