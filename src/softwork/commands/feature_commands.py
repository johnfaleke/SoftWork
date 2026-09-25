"""
Feature creation, modification, and deletion commands.
"""
from __future__ import annotations
from typing import Optional, Dict, Any

from softwork.commands.base import Command
from softwork.core.document import Document
from softwork.core.feature import Feature, BoxFeature, CylinderFeature, MountingPlateFeature, FilletFeature
from softwork.core.transaction import AITransaction, TransactionChange


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
