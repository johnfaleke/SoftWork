"""
Sketch container managing datum plane, 2D geometric entities, and closed profiles.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from softwork.sketch.plane import SketchPlane, StandardPlane
from softwork.sketch.elements import SketchElement, Line2D, Circle2D, Rectangle2D, Polygon2D, Point2D
from softwork.sketch.profile import SketchProfile


@dataclass
class Sketch:
    """
    2D Parametric Sketch container.
    """
    id: str = field(default_factory=lambda: f"sketch_{uuid.uuid4().hex[:8]}")
    name: str = "Sketch001"
    plane: SketchPlane = field(default_factory=SketchPlane)
    elements: List[SketchElement] = field(default_factory=list)
    profiles: List[SketchProfile] = field(default_factory=list)

    def add_element(self, element: SketchElement) -> None:
        self.elements.append(element)
        self.update_profiles()

    def add_rectangle(self, width: float, height: float, center_u: float = 0.0, center_v: float = 0.0, centered: bool = True) -> Rectangle2D:
        rect = Rectangle2D(center_u=center_u, center_v=center_v, width=width, height=height, centered=centered)
        self.add_element(rect)
        return rect

    def add_circle(self, radius: float, center_u: float = 0.0, center_v: float = 0.0) -> Circle2D:
        circle = Circle2D(center=Point2D(center_u, center_v), radius=radius)
        self.add_element(circle)
        return circle

    def add_line(self, start_u: float, start_v: float, end_u: float, end_v: float) -> Line2D:
        line = Line2D(start=Point2D(start_u, start_v), end=Point2D(end_u, end_v))
        self.add_element(line)
        return line

    def update_profiles(self) -> List[SketchProfile]:
        """Detects and generates all closed profiles from the elements in this sketch."""
        self.profiles.clear()
        for el in self.elements:
            if not el.is_construction:
                prof = SketchProfile.from_element(el)
                if prof and prof.is_closed:
                    self.profiles.append(prof)
        return self.profiles

    @property
    def primary_profile(self) -> Optional[SketchProfile]:
        if not self.profiles:
            self.update_profiles()
        return self.profiles[0] if self.profiles else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "plane": {
                "type": self.plane.plane_type.value,
                "origin": [self.plane.origin.x, self.plane.origin.y, self.plane.origin.z],
            },
            "elements": [el.to_dict() for el in self.elements],
        }
