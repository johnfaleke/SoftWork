"""
Strict typed AI Tool Registry for SoftWork.
Executes actions exclusively through the deterministic Command layer.
"""
from __future__ import annotations
from typing import Dict, Any, Callable, List, Optional

from softwork.commands.feature_commands import (
    CreateBoxCommand,
    CreateMountingPlateCommand,
    AddFilletCommand,
)
from softwork.commands.parameter_commands import SetParameterCommand
from softwork.core.document import Document
from softwork.core.transaction import AITransaction


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
