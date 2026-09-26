"""
2D Geometric entities for sketches: Line, Arc, Circle, Rectangle, Polygon.
"""
from __future__ import annotations
import math
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class Point2D:
    u: float
    v: float

    def distance_to(self, other: Point2D) -> float:
        return math.sqrt((self.u - other.u) ** 2 + (self.v - other.v) ** 2)

    def to_tuple(self) -> Tuple[float, float]:
        return (self.u, self.v)


@dataclass
class SketchElement(ABC):
    id: str = field(default_factory=lambda: f"el_{uuid.uuid4().hex[:6]}")
    is_construction: bool = False

    @abstractmethod
    def sample_points(self, resolution: int = 32) -> List[Point2D]:
        """Returns sampled ordered 2D points along the curve/element."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


@dataclass
class Line2D(SketchElement):
    start: Point2D = field(default_factory=lambda: Point2D(0.0, 0.0))
    end: Point2D = field(default_factory=lambda: Point2D(10.0, 0.0))

    def sample_points(self, resolution: int = 32) -> List[Point2D]:
        return [self.start, self.end]

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "line",
            "id": self.id,
            "start": [self.start.u, self.start.v],
            "end": [self.end.u, self.end.v],
            "is_construction": self.is_construction,
        }


@dataclass
class Circle2D(SketchElement):
    center: Point2D = field(default_factory=lambda: Point2D(0.0, 0.0))
    radius: float = 10.0

    def sample_points(self, resolution: int = 32) -> List[Point2D]:
        pts = []
        for i in range(resolution):
            angle = 2.0 * math.pi * i / resolution
            pts.append(Point2D(self.center.u + self.radius * math.cos(angle), self.center.v + self.radius * math.sin(angle)))
        return pts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "circle",
            "id": self.id,
            "center": [self.center.u, self.center.v],
            "radius": self.radius,
            "is_construction": self.is_construction,
        }


@dataclass
class Rectangle2D(SketchElement):
    center_u: float = 0.0
    center_v: float = 0.0
    width: float = 100.0
    height: float = 60.0
    centered: bool = True

    def sample_points(self, resolution: int = 32) -> List[Point2D]:
        if self.centered:
            hw, hh = self.width / 2.0, self.height / 2.0
            u0, u1 = self.center_u - hw, self.center_u + hw
            v0, v1 = self.center_v - hh, self.center_v + hh
        else:
            u0, u1 = self.center_u, self.center_u + self.width
            v0, v1 = self.center_v, self.center_v + self.height
        return [
            Point2D(u0, v0),
            Point2D(u1, v0),
            Point2D(u1, v1),
            Point2D(u0, v1),
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "rectangle",
            "id": self.id,
            "center": [self.center_u, self.center_v],
            "width": self.width,
            "height": self.height,
            "centered": self.centered,
            "is_construction": self.is_construction,
        }


@dataclass
class Polygon2D(SketchElement):
    vertices: List[Point2D] = field(default_factory=list)

    def sample_points(self, resolution: int = 32) -> List[Point2D]:
        return list(self.vertices)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "polygon",
            "id": self.id,
            "vertices": [[p.u, p.v] for p in self.vertices],
            "is_construction": self.is_construction,
        }
