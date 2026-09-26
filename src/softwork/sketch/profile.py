"""
2D closed profile loop detection, validation, and triangulation.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from softwork.sketch.elements import Point2D, SketchElement, Rectangle2D, Circle2D, Polygon2D


@dataclass
class SketchProfile:
    """
    Closed 2D boundary loop ready for extrusion, revolution, or pocketing.
    """
    outer_loop: List[Point2D] = field(default_factory=list)
    inner_loops: List[List[Point2D]] = field(default_factory=list)  # Holes inside the profile

    @property
    def is_closed(self) -> bool:
        return len(self.outer_loop) >= 3

    def area(self) -> float:
        """Calculates signed polygon area (Shoelace formula)."""
        if len(self.outer_loop) < 3:
            return 0.0
        n = len(self.outer_loop)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self.outer_loop[i].u * self.outer_loop[j].v
            area -= self.outer_loop[j].u * self.outer_loop[i].v
        area = abs(area) / 2.0

        # Subtract inner hole areas
        for inner in self.inner_loops:
            if len(inner) >= 3:
                h_area = 0.0
                m = len(inner)
                for i in range(m):
                    j = (i + 1) % m
                    h_area += inner[i].u * inner[j].v
                    h_area -= inner[j].u * inner[i].v
                area -= abs(h_area) / 2.0

        return max(0.0, area)

    @classmethod
    def from_element(cls, element: SketchElement) -> Optional[SketchProfile]:
        if isinstance(element, Rectangle2D):
            pts = element.sample_points()
            return cls(outer_loop=pts)
        elif isinstance(element, Circle2D):
            pts = element.sample_points(32)
            return cls(outer_loop=pts)
        elif isinstance(element, Polygon2D):
            if len(element.vertices) >= 3:
                return cls(outer_loop=list(element.vertices))
        return None
