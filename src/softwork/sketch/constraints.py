"""
2D Geometric Constraints for SoftWork Parametric Sketches.
Defines constraint types: Coincident, Horizontal, Vertical, Distance, Length, Radius, Angle, Parallel, Perpendicular.
"""
from __future__ import annotations
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple

from softwork.sketch.elements import Point2D


class ConstraintType(str, Enum):
    COINCIDENT = "coincident"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DISTANCE = "distance"
    LENGTH = "length"
    RADIUS = "radius"
    ANGLE = "angle"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    FIXED = "fixed"


@dataclass
class Constraint:
    """
    Base geometric constraint linking sketch entities or points.
    """
    id: str = field(default_factory=lambda: f"c_{uuid.uuid4().hex[:8]}")
    name: str = "Constraint"
    constraint_type: ConstraintType = ConstraintType.COINCIDENT
    target_ids: List[str] = field(default_factory=list)
    value: float = 0.0
    is_satisfied: bool = False

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        """
        Calculates residual error (should be 0.0 when constraint is satisfied).
        """
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "constraint_type": self.constraint_type.value,
            "target_ids": self.target_ids,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Constraint:
        ctype = ConstraintType(data.get("constraint_type", "coincident"))
        c_id = data.get("id", f"c_{uuid.uuid4().hex[:8]}")
        name = data.get("name", "Constraint")
        targets = data.get("target_ids", [])
        val = float(data.get("value", 0.0))

        if ctype == ConstraintType.COINCIDENT:
            return CoincidentConstraint(id=c_id, name=name, point_a_id=targets[0], point_b_id=targets[1])
        elif ctype == ConstraintType.HORIZONTAL:
            return HorizontalConstraint(id=c_id, name=name, point_a_id=targets[0], point_b_id=targets[1])
        elif ctype == ConstraintType.VERTICAL:
            return VerticalConstraint(id=c_id, name=name, point_a_id=targets[0], point_b_id=targets[1])
        elif ctype == ConstraintType.DISTANCE:
            return DistanceConstraint(id=c_id, name=name, point_a_id=targets[0], point_b_id=targets[1], distance=val)
        elif ctype == ConstraintType.LENGTH:
            return LengthConstraint(id=c_id, name=name, line_id=targets[0], length=val)
        elif ctype == ConstraintType.RADIUS:
            return RadiusConstraint(id=c_id, name=name, circle_id=targets[0], radius=val)
        elif ctype == ConstraintType.FIXED:
            return FixedConstraint(id=c_id, name=name, point_id=targets[0], fixed_u=val)
        return cls(id=c_id, name=name, constraint_type=ctype, target_ids=targets, value=val)


@dataclass
class CoincidentConstraint(Constraint):
    """Constrains two points to share the exact same coordinates."""
    point_a_id: str = ""
    point_b_id: str = ""

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.COINCIDENT
        self.target_ids = [self.point_a_id, self.point_b_id]
        self.name = f"Coincident({self.point_a_id}, {self.point_b_id})"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        p1 = points.get(self.point_a_id)
        p2 = points.get(self.point_b_id)
        if not p1 or not p2:
            return 0.0
        return math.hypot(p1.u - p2.u, p1.v - p2.v)


@dataclass
class HorizontalConstraint(Constraint):
    """Constrains two points (or a line segment) to have equal V coordinates (horizontal)."""
    point_a_id: str = ""
    point_b_id: str = ""

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.HORIZONTAL
        self.target_ids = [self.point_a_id, self.point_b_id]
        self.name = f"Horizontal({self.point_a_id}, {self.point_b_id})"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        p1 = points.get(self.point_a_id)
        p2 = points.get(self.point_b_id)
        if not p1 or not p2:
            return 0.0
        return abs(p1.v - p2.v)


@dataclass
class VerticalConstraint(Constraint):
    """Constrains two points (or a line segment) to have equal U coordinates (vertical)."""
    point_a_id: str = ""
    point_b_id: str = ""

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.VERTICAL
        self.target_ids = [self.point_a_id, self.point_b_id]
        self.name = f"Vertical({self.point_a_id}, {self.point_b_id})"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        p1 = points.get(self.point_a_id)
        p2 = points.get(self.point_b_id)
        if not p1 or not p2:
            return 0.0
        return abs(p1.u - p2.u)


@dataclass
class DistanceConstraint(Constraint):
    """Constrains Euclidean distance between two points to a specific value."""
    point_a_id: str = ""
    point_b_id: str = ""
    distance: float = 0.0

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.DISTANCE
        self.target_ids = [self.point_a_id, self.point_b_id]
        self.value = self.distance
        self.name = f"Distance({self.point_a_id}, {self.point_b_id}) = {self.distance:.1f}mm"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        p1 = points.get(self.point_a_id)
        p2 = points.get(self.point_b_id)
        if not p1 or not p2:
            return 0.0
        dist = math.hypot(p1.u - p2.u, p1.v - p2.v)
        return abs(dist - self.distance)


@dataclass
class LengthConstraint(Constraint):
    """Constrains length of a Line2D element."""
    line_id: str = ""
    length: float = 0.0

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.LENGTH
        self.target_ids = [self.line_id]
        self.value = self.length
        self.name = f"Length({self.line_id}) = {self.length:.1f}mm"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        line = elements.get(self.line_id)
        if not line or not hasattr(line, "length"):
            return 0.0
        return abs(line.length() - self.length)


@dataclass
class RadiusConstraint(Constraint):
    """Constrains radius of a Circle2D element."""
    circle_id: str = ""
    radius: float = 0.0

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.RADIUS
        self.target_ids = [self.circle_id]
        self.value = self.radius
        self.name = f"Radius({self.circle_id}) = {self.radius:.1f}mm"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        circ = elements.get(self.circle_id)
        if not circ or not hasattr(circ, "radius"):
            return 0.0
        return abs(circ.radius - self.radius)


@dataclass
class FixedConstraint(Constraint):
    """Locks a point to fixed (u, v) coordinates."""
    point_id: str = ""
    fixed_u: float = 0.0
    fixed_v: float = 0.0

    def __post_init__(self) -> None:
        self.constraint_type = ConstraintType.FIXED
        self.target_ids = [self.point_id]
        self.name = f"Fixed({self.point_id} at ({self.fixed_u:.1f}, {self.fixed_v:.1f}))"

    def residual(self, points: Dict[str, Point2D], elements: Dict[str, Any]) -> float:
        p = points.get(self.point_id)
        if not p:
            return 0.0
        return math.hypot(p.u - self.fixed_u, p.v - self.fixed_v)
