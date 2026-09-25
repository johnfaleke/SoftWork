"""
Parametric Feature Model for SoftWork.
"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List

from softwork.cad.backend import CADBackend
from softwork.cad.topology import CADShape
from softwork.core.parameter import Parameter


class FeatureType(str, Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    SKETCH = "sketch"
    EXTRUDE = "extrude"
    CUT = "cut"
    HOLE = "hole"
    HOLE_PATTERN = "hole_pattern"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    MOUNTING_PLATE = "mounting_plate"
    CUSTOM = "custom"


class FeatureStatus(str, Enum):
    VALID = "valid"
    DIRTY = "dirty"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


@dataclass
class Feature(ABC):
    """
    Abstract base class for all parametric CAD features.
    """
    id: str = field(default_factory=lambda: f"feat_{uuid.uuid4().hex[:8]}")
    name: str = ""
    feature_type: FeatureType = FeatureType.CUSTOM
    parameters: Dict[str, Parameter] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: FeatureStatus = FeatureStatus.DIRTY
    error_message: Optional[str] = None
    provenance: str = "user"  # "user", "ai", "script"
    is_suppressed: bool = False
    generated_shape: Optional[CADShape] = None

    def get_parameter(self, param_name: str) -> Parameter:
        if param_name not in self.parameters:
            raise KeyError(f"Feature '{self.name}' has no parameter '{param_name}'")
        return self.parameters[param_name]

    def set_parameter_value(self, param_name: str, value: float, unit: Optional[str] = None) -> None:
        param = self.get_parameter(param_name)
        param.set_value(value, unit)
        self.status = FeatureStatus.DIRTY

    @abstractmethod
    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        """Evaluates geometry for this feature given the CAD backend and dependency shapes."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "feature_type": self.feature_type.value,
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "dependencies": list(self.dependencies),
            "status": self.status.value,
            "provenance": self.provenance,
            "is_suppressed": self.is_suppressed,
        }


class BoxFeature(Feature):
    def __init__(
        self,
        name: str = "Box001",
        width: float = 100.0,
        height: float = 60.0,
        depth: float = 10.0,
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"box_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.BOX,
            provenance=provenance,
        )
        self.parameters = {
            "width": Parameter(name="width", value=width, unit="mm", description="Width along X"),
            "height": Parameter(name="height", value=height, unit="mm", description="Height along Y"),
            "depth": Parameter(name="depth", value=depth, unit="mm", description="Depth / Thickness along Z"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        w = self.parameters["width"].canonical_value
        h = self.parameters["height"].canonical_value
        d = self.parameters["depth"].canonical_value
        shape = backend.create_box(w, h, d, center=True)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class CylinderFeature(Feature):
    def __init__(
        self,
        name: str = "Cylinder001",
        radius: float = 10.0,
        height: float = 50.0,
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"cyl_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.CYLINDER,
            provenance=provenance,
        )
        self.parameters = {
            "radius": Parameter(name="radius", value=radius, unit="mm", description="Cylinder radius"),
            "height": Parameter(name="height", value=height, unit="mm", description="Cylinder height / length"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        r = self.parameters["radius"].canonical_value
        h = self.parameters["height"].canonical_value
        shape = backend.create_cylinder(r, h, center=True)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class MountingPlateFeature(Feature):
    """
    Parametric mounting plate feature combining base plate, corner holes, and fillets.
    """
    def __init__(
        self,
        name: str = "MountingPlate001",
        length: float = 100.0,
        width: float = 60.0,
        thickness: float = 10.0,
        hole_diameter: float = 8.0,
        hole_offset: float = 10.0,
        fillet_radius: float = 0.0,
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"plate_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.MOUNTING_PLATE,
            provenance=provenance,
        )
        self.parameters = {
            "length": Parameter(name="length", value=length, unit="mm", description="Plate length (X)"),
            "width": Parameter(name="width", value=width, unit="mm", description="Plate width (Y)"),
            "thickness": Parameter(name="thickness", value=thickness, unit="mm", description="Plate thickness (Z)"),
            "hole_diameter": Parameter(name="hole_diameter", value=hole_diameter, unit="mm", description="Hole diameter"),
            "hole_offset": Parameter(name="hole_offset", value=hole_offset, unit="mm", description="Hole corner offset"),
            "fillet_radius": Parameter(name="fillet_radius", value=fillet_radius, unit="mm", description="Corner fillet radius"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        l = self.parameters["length"].canonical_value
        w = self.parameters["width"].canonical_value
        t = self.parameters["thickness"].canonical_value
        hd = self.parameters["hole_diameter"].canonical_value
        ho = self.parameters["hole_offset"].canonical_value
        fr = self.parameters["fillet_radius"].canonical_value
        shape = backend.create_plate_with_holes(l, w, t, hd, ho, fr)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class FilletFeature(Feature):
    def __init__(
        self,
        target_feature_id: str,
        radius: float = 2.0,
        name: str = "Fillet001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"fillet_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.FILLET,
            dependencies=[target_feature_id],
            provenance=provenance,
        )
        self.parameters = {
            "radius": Parameter(name="radius", value=radius, unit="mm", description="Fillet radius"),
        }
        self.target_feature_id = target_feature_id

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        if self.target_feature_id not in context_shapes:
            raise ValueError(f"Target shape for fillet '{self.target_feature_id}' not found")
        base_shape = context_shapes[self.target_feature_id]
        r = self.parameters["radius"].canonical_value
        shape = backend.fillet(base_shape, r)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape
