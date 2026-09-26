"""
Feature creation, modification, sketch extrusion, revolution, and pattern commands for SoftWork v0.2.
"""
from __future__ import annotations
from typing import Optional, Dict, Any

from softwork.commands.base import Command
from softwork.core.document import Document
from softwork.core.feature import (
    Feature,
    BoxFeature,
    CylinderFeature,
    MountingPlateFeature,
    FilletFeature,
    ChamferFeature,
    SketchFeature,
    ExtrudeFeature,
    RevolveFeature,
    PatternFeature,
    HoleWizardFeature,
    ShellFeature,
)
from softwork.sketch.sketch import Sketch
from softwork.sketch.plane import SketchPlane, StandardPlane
from softwork.core.transaction import AITransaction, TransactionChange


class CreateSketchCommand(Command):
    def __init__(
        self,
        name: str = "Sketch001",
        plane_type: StandardPlane = StandardPlane.XY,
        provenance: str = "user",
    ) -> None:
        self.name = name
        self.plane_type = plane_type
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        sketch = Sketch(name=self.name, plane=SketchPlane.from_standard(self.plane_type))
        feature = SketchFeature(sketch=sketch, name=self.name, provenance=self.provenance)

        tx = AITransaction(
            title=f"Create Sketch ({self.plane_type.value})",
            affected_features=[feature.id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Created {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class ExtrudeSketchCommand(Command):
    def __init__(
        self,
        sketch_feature_id: str,
        distance: float = 25.0,
        name: str = "Extrude001",
        provenance: str = "user",
    ) -> None:
        self.sketch_feature_id = sketch_feature_id
        self.distance = distance
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        sk_feat = document.get_feature(self.sketch_feature_id)
        if not isinstance(sk_feat, SketchFeature):
            raise ValueError(f"Feature '{self.sketch_feature_id}' is not a SketchFeature")

        feature = ExtrudeFeature(
            target_sketch_feature=sk_feat,
            distance=self.distance,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Extrude {sk_feat.name} ({self.distance}mm)",
            affected_features=[feature.id, sk_feat.id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Extruded {sk_feat.name} by {self.distance}mm", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class RevolveSketchCommand(Command):
    def __init__(
        self,
        sketch_feature_id: str,
        angle_deg: float = 360.0,
        axis: str = "Y",
        name: str = "Revolve001",
        provenance: str = "user",
    ) -> None:
        self.sketch_feature_id = sketch_feature_id
        self.angle_deg = angle_deg
        self.axis = axis
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        sk_feat = document.get_feature(self.sketch_feature_id)
        if not isinstance(sk_feat, SketchFeature):
            raise ValueError(f"Feature '{self.sketch_feature_id}' is not a SketchFeature")

        feature = RevolveFeature(
            target_sketch_feature=sk_feat,
            angle_deg=self.angle_deg,
            axis=self.axis,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Revolve {sk_feat.name} ({self.angle_deg} deg)",
            affected_features=[feature.id, sk_feat.id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Revolved {sk_feat.name} by {self.angle_deg} deg", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class AddPatternCommand(Command):
    def __init__(
        self,
        target_feature_id: str,
        count_x: int = 3,
        count_y: int = 1,
        spacing_x: float = 20.0,
        spacing_y: float = 0.0,
        name: str = "Pattern001",
        provenance: str = "user",
    ) -> None:
        self.target_feature_id = target_feature_id
        self.count_x = count_x
        self.count_y = count_y
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = PatternFeature(
            target_feature_id=self.target_feature_id,
            count_x=self.count_x,
            count_y=self.count_y,
            spacing_x=self.spacing_x,
            spacing_y=self.spacing_y,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Pattern ({self.count_x}x{self.count_y})",
            affected_features=[feature.id, self.target_feature_id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Patterned {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class AddChamferCommand(Command):
    def __init__(
        self,
        target_feature_id: str,
        distance: float = 1.0,
        name: str = "Chamfer001",
        provenance: str = "user",
    ) -> None:
        self.target_feature_id = target_feature_id
        self.distance = distance
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = ChamferFeature(
            target_feature_id=self.target_feature_id,
            distance=self.distance,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Add Chamfer ({self.distance}mm)",
            affected_features=[feature.id, self.target_feature_id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Added chamfer {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class CreateBoxCommand(Command):
    def __init__(
        self,
        width: float,
        height: float,
        depth: float,
        name: str = "Box001",
        provenance: str = "user",
    ) -> None:
        self.width = width
        self.height = height
        self.depth = depth
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = BoxFeature(
            name=self.name,
            width=self.width,
            height=self.height,
            depth=self.depth,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Create {self.name}",
            affected_features=[feature.id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Created box {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class CreateMountingPlateCommand(Command):
    def __init__(
        self,
        length: float,
        width: float,
        thickness: float,
        hole_diameter: float = 8.0,
        hole_offset: float = 10.0,
        fillet_radius: float = 0.0,
        name: str = "MountingPlate001",
        provenance: str = "user",
    ) -> None:
        self.length = length
        self.width = width
        self.thickness = thickness
        self.hole_diameter = hole_diameter
        self.hole_offset = hole_offset
        self.fillet_radius = fillet_radius
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = MountingPlateFeature(
            name=self.name,
            length=self.length,
            width=self.width,
            thickness=self.thickness,
            hole_diameter=self.hole_diameter,
            hole_offset=self.hole_offset,
            fillet_radius=self.fillet_radius,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Create {self.name}",
            affected_features=[feature.id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Created plate {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class AddFilletCommand(Command):
    def __init__(
        self,
        target_feature_id: str,
        radius: float,
        name: str = "Fillet001",
        provenance: str = "user",
    ) -> None:
        self.target_feature_id = target_feature_id
        self.radius = radius
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = FilletFeature(
            target_feature_id=self.target_feature_id,
            radius=self.radius,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Add Fillet ({self.radius}mm)",
            affected_features=[feature.id, self.target_feature_id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Added fillet {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class AddHoleWizardCommand(Command):
    def __init__(
        self,
        target_feature_id: str,
        metric_size: str = "M8",
        hole_type: str = "simple",
        depth: float = 20.0,
        pos_u: float = 0.0,
        pos_v: float = 0.0,
        name: str = "Hole001",
        provenance: str = "user",
    ) -> None:
        self.target_feature_id = target_feature_id
        self.metric_size = metric_size
        self.hole_type = hole_type
        self.depth = depth
        self.pos_u = pos_u
        self.pos_v = pos_v
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = HoleWizardFeature(
            target_feature_id=self.target_feature_id,
            metric_size=self.metric_size,
            hole_type=self.hole_type,
            depth=self.depth,
            pos_u=self.pos_u,
            pos_v=self.pos_v,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Add {self.metric_size} {self.hole_type.title()} Hole",
            affected_features=[feature.id, self.target_feature_id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Added {self.metric_size} hole", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx


class AddShellCommand(Command):
    def __init__(
        self,
        target_feature_id: str,
        wall_thickness: float = 2.0,
        name: str = "Shell001",
        provenance: str = "user",
    ) -> None:
        self.target_feature_id = target_feature_id
        self.wall_thickness = wall_thickness
        self.name = name
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        part = document.active_part
        feature = ShellFeature(
            target_feature_id=self.target_feature_id,
            wall_thickness=self.wall_thickness,
            name=self.name,
            provenance=self.provenance,
        )

        tx = AITransaction(
            title=f"Shell ({self.wall_thickness}mm wall)",
            affected_features=[feature.id, self.target_feature_id],
        )

        def do() -> None:
            document.add_feature(feature, part)

        def undo() -> None:
            part.remove_feature(feature.id)
            document.dependency_graph.remove_node(feature.id)
            document.recompute()

        do()
        tx.changes.append(TransactionChange(description=f"Shelled solid {feature.name}", undo_action=undo, redo_action=do))
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx
