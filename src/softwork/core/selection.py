"""
Selection model and active context for UI and AI agent.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class SelectionContext:
    selected_part_id: Optional[str] = None
    selected_feature_ids: List[str] = field(default_factory=list)
    selected_entity_ids: List[str] = field(default_factory=list)  # faces, edges, vertices

    def clear(self) -> None:
        self.selected_part_id = None
        self.selected_feature_ids.clear()
        self.selected_entity_ids.clear()

    def select_feature(self, feature_id: str, additive: bool = False) -> None:
        if not additive:
            self.selected_feature_ids.clear()
        if feature_id not in self.selected_feature_ids:
            self.selected_feature_ids.append(feature_id)

    @property
    def primary_feature_id(self) -> Optional[str]:
        return self.selected_feature_ids[0] if self.selected_feature_ids else None
