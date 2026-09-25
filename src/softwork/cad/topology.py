"""
CAD Topology structures and persistent entity naming abstractions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class TopologyType(str, Enum):
    COMPOUND = "compound"
    COMPSOLID = "compsolid"
    SOLID = "solid"
    SHELL = "shell"
    FACE = "face"
    WIRE = "wire"
    EDGE = "edge"
    VERTEX = "vertex"


@dataclass
class TopologyEntity:
    id: str
    entity_type: TopologyType
    name: str = ""
    feature_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List[TopologyEntity] = field(default_factory=list)


@dataclass
class CADShape:
    """Wrapper around geometric/topological solid representation."""
    id: str
    shape_type: str
    native_handle: Optional[Any] = None
    volume: float = 0.0
    surface_area: float = 0.0
    is_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
