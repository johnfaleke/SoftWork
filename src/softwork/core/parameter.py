"""
Strongly-typed parametric dimensions and expressions.
"""
from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Union


class UnitType(str, Enum):
    MILLIMETER = "mm"
    CENTIMETER = "cm"
    METER = "m"
    INCH = "in"
    FOOT = "ft"
    DEGREE = "deg"
    RADIAN = "rad"
    COUNT = "count"
    RATIO = "ratio"


# Canonical internal units are mm for length, rad for angle
UNIT_TO_CANONICAL: Dict[str, float] = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
    "ft": 304.8,
    "deg": math.pi / 180.0,
    "rad": 1.0,
    "count": 1.0,
    "ratio": 1.0,
}


@dataclass
class Parameter:
    """
    Parametric dimension supporting units, expressions, constraints, and provenance.
    """
    name: str
    value: float
    unit: str = "mm"
    expression: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    is_read_only: bool = False
    provenance: str = "user"  # "user", "ai", "derived"

    @property
    def canonical_value(self) -> float:
        """Returns the value converted to internal canonical units (mm, rad)."""
        factor = UNIT_TO_CANONICAL.get(self.unit.lower(), 1.0)
        return self.value * factor

    def set_value(self, new_value: float, unit: Optional[str] = None) -> None:
        if self.is_read_only:
            raise ValueError(f"Parameter '{self.name}' is read-only")
        if unit:
            self.unit = unit
        if self.min_value is not None and new_value < self.min_value:
            raise ValueError(f"Value {new_value} for '{self.name}' is below minimum {self.min_value}")
        if self.max_value is not None and new_value > self.max_value:
            raise ValueError(f"Value {new_value} for '{self.name}' exceeds maximum {self.max_value}")
        self.value = float(new_value)

    @classmethod
    def from_string(cls, name: str, text: str, default_unit: str = "mm") -> Parameter:
        """Parses inputs such as '100mm', '15.5 in', '45 deg', '10'."""
        text = text.strip()
        match = re.match(r"^([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)$", text)
        if match:
            val = float(match.group(1))
            u = match.group(2) if match.group(2) else default_unit
            return cls(name=name, value=val, unit=u)
        raise ValueError(f"Cannot parse parameter from string: '{text}'")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "expression": self.expression,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "description": self.description,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Parameter:
        return cls(
            name=data["name"],
            value=float(data["value"]),
            unit=data.get("unit", "mm"),
            expression=data.get("expression"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            description=data.get("description", ""),
            provenance=data.get("provenance", "user"),
        )
