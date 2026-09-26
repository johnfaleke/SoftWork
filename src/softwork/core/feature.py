"""
Parametric Feature Model for SoftWork v0.2.
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
from softwork.sketch.sketch import Sketch
from softwork.sketch.profile import SketchProfile


class FeatureType(str, Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    SKETCH = "sketch"
    EXTRUDE = "extrude"
    REVOLVE = "revolve"
    CUT = "cut"
    HOLE = "hole"
    HOLE_WIZARD = "hole_wizard"
    SHELL = "shell"
    HOLE_PATTERN = "hole_pattern"
    PATTERN = "pattern"
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


class SketchFeature(Feature):
    """
    First-class Sketch feature holding 2D geometry and profiles.
    """
    def __init__(
        self,
        sketch: Optional[Sketch] = None,
        name: str = "Sketch001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"skfeat_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.SKETCH,
            provenance=provenance,
        )
        self.sketch = sketch or Sketch(name=name)

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        # A sketch generates a 2D wireframe placeholder shape
        self.status = FeatureStatus.VALID
        return CADShape(
            id=f"shape_{self.id}",
            shape_type="sketch_wire",
            volume=0.0,
            is_valid=True,
            metadata={"sketch": self.sketch},
        )

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["sketch_data"] = self.sketch.to_dict()
        return d


class ExtrudeFeature(Feature):
    """
    Extrudes a parent SketchFeature profile into a 3D solid.
    """
    def __init__(
        self,
        target_sketch_feature: SketchFeature,
        distance: float = 25.0,
        operation: str = "add",
        name: str = "Extrude001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"ext_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.EXTRUDE,
            dependencies=[target_sketch_feature.id],
            provenance=provenance,
        )
        self.target_sketch_feature = target_sketch_feature
        self.operation = operation
        self.parameters = {
            "distance": Parameter(name="distance", value=distance, unit="mm", description="Extrusion distance / thickness"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        profile = self.target_sketch_feature.sketch.primary_profile
        if not profile:
            raise ValueError(f"Sketch '{self.target_sketch_feature.name}' does not contain any closed profiles to extrude")

        dist = self.parameters["distance"].canonical_value
        shape = backend.extrude_profile(profile, dist, self.target_sketch_feature.sketch.plane)

        # Check for prior base solids to combine with
        base_solid = None
        for feat_id, s in context_shapes.items():
            if feat_id != self.target_sketch_feature.id and s.shape_type != "sketch_wire" and s.volume > 0:
                base_solid = s

        if base_solid is not None:
            if self.operation == "add":
                shape = backend.union(base_solid, shape)
            elif self.operation == "cut":
                shape = backend.cut(base_solid, shape)

        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class RevolveFeature(Feature):
    """
    Revolves a parent SketchFeature profile around an axis into an axis-symmetric 3D solid.
    """
    def __init__(
        self,
        target_sketch_feature: SketchFeature,
        angle_deg: float = 360.0,
        axis: str = "Y",
        operation: str = "add",
        name: str = "Revolve001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"rev_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.REVOLVE,
            dependencies=[target_sketch_feature.id],
            provenance=provenance,
        )
        self.target_sketch_feature = target_sketch_feature
        self.axis = axis
        self.operation = operation
        self.parameters = {
            "angle": Parameter(name="angle", value=angle_deg, unit="deg", description="Revolution angle in degrees"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        profile = self.target_sketch_feature.sketch.primary_profile
        if not profile:
            raise ValueError(f"Sketch '{self.target_sketch_feature.name}' has no closed profile to revolve")

        angle_deg = self.parameters["angle"].value
        shape = backend.revolve_profile(profile, angle_deg, axis=self.axis, plane=self.target_sketch_feature.sketch.plane)

        base_solid = None
        for feat_id, s in context_shapes.items():
            if feat_id != self.target_sketch_feature.id and s.shape_type != "sketch_wire" and s.volume > 0:
                base_solid = s

        if base_solid is not None and self.operation == "add":
            shape = backend.union(base_solid, shape)

        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class PatternFeature(Feature):
    """
    Creates repeated array patterns of parent solid features.
    """
    def __init__(
        self,
        target_feature_id: str,
        count_x: int = 3,
        count_y: int = 1,
        spacing_x: float = 20.0,
        spacing_y: float = 0.0,
        name: str = "Pattern001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"pat_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.PATTERN,
            dependencies=[target_feature_id],
            provenance=provenance,
        )
        self.target_feature_id = target_feature_id
        self.parameters = {
            "count_x": Parameter(name="count_x", value=float(count_x), unit="count"),
            "count_y": Parameter(name="count_y", value=float(count_y), unit="count"),
            "spacing_x": Parameter(name="spacing_x", value=spacing_x, unit="mm"),
            "spacing_y": Parameter(name="spacing_y", value=spacing_y, unit="mm"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        if self.target_feature_id not in context_shapes:
            raise ValueError(f"Target shape '{self.target_feature_id}' for pattern not found")
        base = context_shapes[self.target_feature_id]
        cx = int(self.parameters["count_x"].value)
        cy = int(self.parameters["count_y"].value)
        sx = self.parameters["spacing_x"].canonical_value
        sy = self.parameters["spacing_y"].canonical_value
        shape = backend.pattern_linear(base, cx, cy, sx, sy)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class ChamferFeature(Feature):
    """
    Applies edge chamfers with a distance parameter.
    """
    def __init__(
        self,
        target_feature_id: str,
        distance: float = 1.0,
        name: str = "Chamfer001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"chamf_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.CHAMFER,
            dependencies=[target_feature_id],
            provenance=provenance,
        )
        self.target_feature_id = target_feature_id
        self.parameters = {
            "distance": Parameter(name="distance", value=distance, unit="mm", description="Chamfer distance"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        if self.target_feature_id not in context_shapes:
            raise ValueError(f"Target shape '{self.target_feature_id}' for chamfer not found")
        base = context_shapes[self.target_feature_id]
        dist = self.parameters["distance"].canonical_value
        shape = backend.chamfer(base, dist)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


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


class HoleWizardFeature(Feature):
    """
    Standard ISO metric hole feature supporting Simple, Counterbore, and Countersink holes.
    """
    def __init__(
        self,
        target_feature_id: str,
        metric_size: str = "M8",
        hole_type: str = "simple",
        depth: float = 20.0,
        pos_u: float = 0.0,
        pos_v: float = 0.0,
        name: str = "Hole001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"hw_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.HOLE_WIZARD,
            dependencies=[target_feature_id],
            provenance=provenance,
        )
        self.target_feature_id = target_feature_id
        self.metric_size = metric_size.upper()
        self.hole_type = hole_type.lower()

        # Standard ISO metric hole lookup table
        std_dims: Dict[str, Tuple[float, float, float]] = {
            "M3": (3.4, 6.0, 3.0),
            "M4": (4.5, 8.0, 4.0),
            "M5": (5.5, 9.5, 5.0),
            "M6": (6.6, 11.0, 6.0),
            "M8": (9.0, 15.0, 8.0),
            "M10": (11.0, 18.0, 10.0),
            "M12": (13.5, 20.0, 12.0),
            "M16": (17.5, 26.0, 16.0),
        }
        dia, cb_dia, cb_dp = std_dims.get(self.metric_size, (8.0, 14.0, 6.0))

        self.parameters = {
            "diameter": Parameter(name="diameter", value=dia, unit="mm", description="Hole clearance diameter"),
            "depth": Parameter(name="depth", value=depth, unit="mm", description="Hole depth"),
            "cb_diameter": Parameter(name="cb_diameter", value=cb_dia, unit="mm", description="Counterbore diameter"),
            "cb_depth": Parameter(name="cb_depth", value=cb_dp, unit="mm", description="Counterbore depth"),
            "pos_u": Parameter(name="pos_u", value=pos_u, unit="mm", description="Position U"),
            "pos_v": Parameter(name="pos_v", value=pos_v, unit="mm", description="Position V"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        if self.target_feature_id not in context_shapes:
            raise ValueError(f"Target shape '{self.target_feature_id}' for Hole Wizard not found")
        base_shape = context_shapes[self.target_feature_id]

        dia = self.parameters["diameter"].canonical_value
        dp = self.parameters["depth"].canonical_value
        cb_dia = self.parameters["cb_diameter"].canonical_value
        cb_dp = self.parameters["cb_depth"].canonical_value
        pu = self.parameters["pos_u"].canonical_value
        pv = self.parameters["pos_v"].canonical_value

        hole_tool = backend.create_hole_tool(
            hole_type=self.hole_type,
            diameter=dia,
            depth=dp,
            cb_diameter=cb_dia,
            cb_depth=cb_dp,
            pos_u=pu,
            pos_v=pv,
        )
        shape = backend.cut(base_shape, hole_tool)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape


class ShellFeature(Feature):
    """
    Hollows a target solid leaving a specified uniform wall thickness.
    """
    def __init__(
        self,
        target_feature_id: str,
        wall_thickness: float = 2.0,
        name: str = "Shell001",
        id: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        super().__init__(
            id=id or f"shell_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_type=FeatureType.SHELL,
            dependencies=[target_feature_id],
            provenance=provenance,
        )
        self.target_feature_id = target_feature_id
        self.parameters = {
            "wall_thickness": Parameter(name="wall_thickness", value=wall_thickness, unit="mm", description="Wall thickness"),
        }

    def evaluate(self, backend: CADBackend, context_shapes: Dict[str, CADShape]) -> CADShape:
        if self.target_feature_id not in context_shapes:
            raise ValueError(f"Target shape '{self.target_feature_id}' for Shell not found")
        base_shape = context_shapes[self.target_feature_id]
        wt = self.parameters["wall_thickness"].canonical_value
        shape = backend.shell_solid(base_shape, wall_thickness=wt)
        self.generated_shape = shape
        self.status = FeatureStatus.VALID
        return shape
