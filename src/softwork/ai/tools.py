"""
Strict typed AI Tool Registry for SoftWork v0.2.
Executes actions exclusively through the deterministic Command layer.
"""
from __future__ import annotations
from typing import Dict, Any, Callable, List, Optional

from softwork.commands.feature_commands import (
    CreateBoxCommand,
    CreateMountingPlateCommand,
    AddFilletCommand,
    AddChamferCommand,
    CreateSketchCommand,
    ExtrudeSketchCommand,
    RevolveSketchCommand,
    AddPatternCommand,
    AddHoleWizardCommand,
    AddShellCommand,
    AddSketchRectangleCommand,
    AddSketchCircleCommand,
)
from softwork.commands.parameter_commands import SetParameterCommand
from softwork.core.document import Document
from softwork.core.feature import SketchFeature
from softwork.core.transaction import AITransaction
from softwork.sketch.plane import StandardPlane


class ToolRegistry:
    """
    Registry of available CAD agent tools and their strict schemas.
    """

    def __init__(self, document: Document) -> None:
        self.document = document
        self._tools: Dict[str, Callable[[Dict[str, Any]], AITransaction]] = {}
        self._schemas: List[Dict[str, Any]] = []
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        # 1. Sketch creation
        self.register(
            name="sketch.create",
            description="Create a new 2D sketch on a plane (XY, XZ, or YZ)",
            parameters={
                "type": "object",
                "properties": {
                    "plane": {"type": "string", "enum": ["XY", "XZ", "YZ"], "default": "XY"},
                    "name": {"type": "string", "default": "Sketch001"},
                },
            },
            handler=lambda args: CreateSketchCommand(
                name=args.get("name", "Sketch001"),
                plane_type=StandardPlane(args.get("plane", "XY")),
                provenance="ai",
            ).execute(self.document),
        )

        # 2. Sketch add rectangle
        self.register(
            name="sketch.add_rectangle",
            description="Add a 2D rectangle profile to an existing sketch",
            parameters={
                "type": "object",
                "properties": {
                    "sketch_id": {"type": "string", "description": "ID or name of sketch feature"},
                    "width": {"type": "number", "description": "Width in mm"},
                    "height": {"type": "number", "description": "Height in mm"},
                    "centered": {"type": "boolean", "default": True},
                },
                "required": ["width", "height"],
            },
            handler=self._handle_sketch_add_rectangle,
        )

        # 3. Sketch add circle
        self.register(
            name="sketch.add_circle",
            description="Add a 2D circle profile to an existing sketch",
            parameters={
                "type": "object",
                "properties": {
                    "sketch_id": {"type": "string", "description": "ID or name of sketch feature"},
                    "radius": {"type": "number", "description": "Circle radius in mm"},
                },
                "required": ["radius"],
            },
            handler=self._handle_sketch_add_circle,
        )

        # 4. Feature extrude
        self.register(
            name="feature.extrude",
            description="Extrude a 2D sketch profile into a 3D solid",
            parameters={
                "type": "object",
                "properties": {
                    "sketch_id": {"type": "string", "description": "Target sketch feature ID or name"},
                    "distance": {"type": "number", "description": "Extrusion distance in mm"},
                    "name": {"type": "string", "default": "Extrude001"},
                },
                "required": ["distance"],
            },
            handler=self._handle_feature_extrude,
        )

        # 5. Feature revolve
        self.register(
            name="feature.revolve",
            description="Revolve a 2D sketch profile around an axis by a given angle",
            parameters={
                "type": "object",
                "properties": {
                    "sketch_id": {"type": "string", "description": "Target sketch feature ID or name"},
                    "angle_deg": {"type": "number", "default": 360.0},
                    "axis": {"type": "string", "default": "Y"},
                    "name": {"type": "string", "default": "Revolve001"},
                },
            },
            handler=self._handle_feature_revolve,
        )

        # 6. Feature box
        self.register(
            name="feature.create_box",
            description="Create a 3D box solid feature",
            parameters={
                "type": "object",
                "properties": {
                    "width": {"type": "number", "description": "Width in mm"},
                    "height": {"type": "number", "description": "Height in mm"},
                    "depth": {"type": "number", "description": "Depth / Thickness in mm"},
                    "name": {"type": "string", "default": "Box001"},
                },
                "required": ["width", "height", "depth"],
            },
            handler=lambda args: CreateBoxCommand(
                width=float(args["width"]),
                height=float(args["height"]),
                depth=float(args["depth"]),
                name=args.get("name", "Box001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 7. Feature mounting plate
        self.register(
            name="feature.create_plate",
            description="Create a parametric mounting plate with 4 corner holes and optional outer fillets",
            parameters={
                "type": "object",
                "properties": {
                    "length": {"type": "number", "description": "Length (X) in mm"},
                    "width": {"type": "number", "description": "Width (Y) in mm"},
                    "thickness": {"type": "number", "description": "Thickness (Z) in mm"},
                    "hole_diameter": {"type": "number", "default": 8.0},
                    "hole_offset": {"type": "number", "default": 10.0},
                    "fillet_radius": {"type": "number", "default": 0.0},
                    "name": {"type": "string", "default": "MountingPlate001"},
                },
                "required": ["length", "width", "thickness"],
            },
            handler=lambda args: CreateMountingPlateCommand(
                length=float(args["length"]),
                width=float(args["width"]),
                thickness=float(args["thickness"]),
                hole_diameter=float(args.get("hole_diameter", 8.0)),
                hole_offset=float(args.get("hole_offset", 10.0)),
                fillet_radius=float(args.get("fillet_radius", 0.0)),
                name=args.get("name", "MountingPlate001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 8. Feature pattern
        self.register(
            name="feature.pattern",
            description="Create a repeated linear array pattern of a solid feature",
            parameters={
                "type": "object",
                "properties": {
                    "target_feature_id": {"type": "string"},
                    "count_x": {"type": "integer", "default": 3},
                    "count_y": {"type": "integer", "default": 1},
                    "spacing_x": {"type": "number", "default": 20.0},
                    "spacing_y": {"type": "number", "default": 0.0},
                    "name": {"type": "string", "default": "Pattern001"},
                },
                "required": ["target_feature_id"],
            },
            handler=lambda args: AddPatternCommand(
                target_feature_id=args["target_feature_id"],
                count_x=int(args.get("count_x", 3)),
                count_y=int(args.get("count_y", 1)),
                spacing_x=float(args.get("spacing_x", 20.0)),
                spacing_y=float(args.get("spacing_y", 0.0)),
                name=args.get("name", "Pattern001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 9. Feature chamfer
        self.register(
            name="feature.chamfer",
            description="Apply a chamfer to edges with given distance in mm",
            parameters={
                "type": "object",
                "properties": {
                    "target_feature_id": {"type": "string"},
                    "distance": {"type": "number", "default": 1.0},
                    "name": {"type": "string", "default": "Chamfer001"},
                },
                "required": ["target_feature_id"],
            },
            handler=lambda args: AddChamferCommand(
                target_feature_id=args["target_feature_id"],
                distance=float(args.get("distance", 1.0)),
                name=args.get("name", "Chamfer001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 10. Feature Hole Wizard
        self.register(
            name="feature.hole_wizard",
            description="Add standard ISO metric hole (M3 to M16) with simple or counterbore profile",
            parameters={
                "type": "object",
                "properties": {
                    "target_feature_id": {"type": "string"},
                    "metric_size": {"type": "string", "default": "M8"},
                    "hole_type": {"type": "string", "enum": ["simple", "counterbore", "countersink"], "default": "simple"},
                    "depth": {"type": "number", "default": 20.0},
                    "pos_u": {"type": "number", "default": 0.0},
                    "pos_v": {"type": "number", "default": 0.0},
                    "name": {"type": "string", "default": "Hole001"},
                },
                "required": ["target_feature_id"],
            },
            handler=lambda args: AddHoleWizardCommand(
                target_feature_id=args["target_feature_id"],
                metric_size=args.get("metric_size", "M8"),
                hole_type=args.get("hole_type", "simple"),
                depth=float(args.get("depth", 20.0)),
                pos_u=float(args.get("pos_u", 0.0)),
                pos_v=float(args.get("pos_v", 0.0)),
                name=args.get("name", "Hole001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 11. Feature Shell
        self.register(
            name="feature.shell",
            description="Hollow a solid body leaving uniform wall thickness in mm",
            parameters={
                "type": "object",
                "properties": {
                    "target_feature_id": {"type": "string"},
                    "wall_thickness": {"type": "number", "default": 2.0},
                    "name": {"type": "string", "default": "Shell001"},
                },
                "required": ["target_feature_id"],
            },
            handler=lambda args: AddShellCommand(
                target_feature_id=args["target_feature_id"],
                wall_thickness=float(args.get("wall_thickness", 2.0)),
                name=args.get("name", "Shell001"),
                provenance="ai",
            ).execute(self.document),
        )

        # 12. Parameter modification
        self.register(
            name="parameter.set",
            description="Modify a parametric dimension on an existing feature while preserving dependencies",
            parameters={
                "type": "object",
                "properties": {
                    "feature_id": {"type": "string", "description": "ID or name of the target feature"},
                    "parameter_name": {"type": "string", "description": "Name of parameter to modify"},
                    "value": {"type": "number", "description": "New parameter value in canonical units"},
                    "unit": {"type": "string", "default": "mm"},
                },
                "required": ["feature_id", "parameter_name", "value"],
            },
            handler=lambda args: SetParameterCommand(
                feature_id=args["feature_id"],
                parameter_name=args["parameter_name"],
                new_value=float(args["value"]),
                unit=args.get("unit"),
                provenance="ai",
            ).execute(self.document),
        )

        # 11. Export STEP
        self.register(
            name="export.step",
            description="Export the active solid model to STEP format",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Target export file path"},
                },
                "required": ["filepath"],
            },
            handler=self._handle_export_step,
        )

    def _find_sketch_feature(self, sketch_id: Optional[str] = None) -> SketchFeature:
        if sketch_id:
            feat = self.document.get_feature(sketch_id)
            if isinstance(feat, SketchFeature):
                return feat
        for f in reversed(self.document.active_part.features):
            if isinstance(f, SketchFeature):
                return f
        # Auto-create a sketch feature on XY if none exists
        CreateSketchCommand(name="Sketch_XY", plane_type=StandardPlane.XY, provenance="ai").execute(self.document)
        sk_feat = self.document.active_part.features[-1]
        if isinstance(sk_feat, SketchFeature):
            return sk_feat
        raise ValueError("No active Sketch feature found")

    def _handle_sketch_add_rectangle(self, args: Dict[str, Any]) -> AITransaction:
        sk_feat = self._find_sketch_feature(args.get("sketch_id"))
        w = float(args["width"])
        h = float(args["height"])
        centered = bool(args.get("centered", True))
        return AddSketchRectangleCommand(
            sketch_feature_id=sk_feat.id,
            width=w,
            height=h,
            centered=centered,
            provenance="ai",
        ).execute(self.document)

    def _handle_sketch_add_circle(self, args: Dict[str, Any]) -> AITransaction:
        sk_feat = self._find_sketch_feature(args.get("sketch_id"))
        r = float(args["radius"])
        return AddSketchCircleCommand(
            sketch_feature_id=sk_feat.id,
            radius=r,
            provenance="ai",
        ).execute(self.document)

    def _handle_feature_extrude(self, args: Dict[str, Any]) -> AITransaction:
        sk_feat = self._find_sketch_feature(args.get("sketch_id"))
        if not sk_feat.sketch.elements:
            sk_feat.sketch.add_rectangle(50.0, 30.0, centered=True)
            self.document.recompute()
        dist = float(args.get("distance", 25.0))
        return ExtrudeSketchCommand(
            sketch_feature_id=sk_feat.id,
            distance=dist,
            name=args.get("name", "Extrude001"),
            provenance="ai",
        ).execute(self.document)

    def _handle_feature_revolve(self, args: Dict[str, Any]) -> AITransaction:
        sk_feat = self._find_sketch_feature(args.get("sketch_id"))
        ang = float(args.get("angle_deg", 360.0))
        axis = args.get("axis", "Y")
        return RevolveSketchCommand(
            sketch_feature_id=sk_feat.id,
            angle_deg=ang,
            axis=axis,
            name=args.get("name", "Revolve001"),
            provenance="ai",
        ).execute(self.document)

    def _handle_export_step(self, args: Dict[str, Any]) -> AITransaction:
        solid = self.document.active_part.active_solid
        if solid is not None:
            self.document.backend.export_step(solid, args["filepath"])
        tx = AITransaction(title=f"Export STEP to {args['filepath']}", is_committed=True)
        return tx

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], AITransaction],
    ) -> None:
        self._tools[name] = handler
        self._schemas.append({"name": name, "description": description, "parameters": parameters})

    def get_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> AITransaction:
        if tool_name not in self._tools:
            raise ValueError(f"Unknown CAD tool: '{tool_name}'")
        return self._tools[tool_name](arguments)
