"""
Parameter modification commands for SoftWork.
"""
from __future__ import annotations
from typing import Optional

from softwork.commands.base import Command
from softwork.core.document import Document
from softwork.core.transaction import AITransaction, TransactionChange


class SetParameterCommand(Command):
    def __init__(
        self,
        feature_id: str,
        parameter_name: str,
        new_value: float,
        unit: Optional[str] = None,
        provenance: str = "user",
    ) -> None:
        self.feature_id = feature_id
        self.parameter_name = parameter_name
        self.new_value = new_value
        self.unit = unit
        self.provenance = provenance

    def execute(self, document: Document) -> AITransaction:
        feature = document.get_feature(self.feature_id)
        if feature is None:
            raise KeyError(f"Feature '{self.feature_id}' not found in document")

        param = feature.get_parameter(self.parameter_name)
        old_value = param.value
        old_unit = param.unit

        # Find dependent features that will be preserved / regenerated
        dependents = list(document.dependency_graph.get_dependents(feature.id))
        all_features = [f.id for p in document.parts for f in p.features]
        preserved = [f for f in all_features if f != feature.id and f not in dependents]

        tx = AITransaction(
            title=f"Set {feature.name}.{self.parameter_name} = {self.new_value}{self.unit or old_unit}",
            affected_features=[feature.id] + dependents,
            preserved_features=preserved,
        )

        def do() -> None:
            feature.set_parameter_value(self.parameter_name, self.new_value, self.unit)
            document.recompute()

        def undo() -> None:
            feature.set_parameter_value(self.parameter_name, old_value, old_unit)
            document.recompute()

        do()
        tx.changes.append(
            TransactionChange(
                description=f"Changed {feature.name}.{self.parameter_name} from {old_value} to {self.new_value}",
                undo_action=undo,
                redo_action=do,
            )
        )
        tx.is_committed = True
        document.history.push_transaction(tx)
        return tx
