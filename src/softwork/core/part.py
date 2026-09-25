"""
Part container representing an individual mechanical component.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from softwork.core.feature import Feature
from softwork.core.parameter import Parameter
from softwork.cad.topology import CADShape


@dataclass
class Part:
    """
    Parametric Part representing an engineering solid with its feature history.
    """
    id: str = field(default_factory=lambda: f"part_{uuid.uuid4().hex[:8]}")
    name: str = "Part001"
    features: List[Feature] = field(default_factory=list)
    parameters: Dict[str, Parameter] = field(default_factory=dict)
    active_solid: Optional[CADShape] = None
    color: str = "#3B82F6"  # Soft modern blue

    def add_feature(self, feature: Feature) -> None:
        self.features.append(feature)

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        for f in self.features:
            if f.id == feature_id or f.name == feature_id:
                return f
        return None

    def remove_feature(self, feature_id: str) -> bool:
        for i, f in enumerate(self.features):
            if f.id == feature_id:
                self.features.pop(i)
                return True
        return False
