"""
Core parametric CAD and document subsystems.
"""
from softwork.core.parameter import Parameter, UnitType
from softwork.core.feature import (
    Feature,
    FeatureType,
    FeatureStatus,
    BoxFeature,
    CylinderFeature,
    MountingPlateFeature,
    FilletFeature,
    ChamferFeature,
    SketchFeature,
    ExtrudeFeature,
    RevolveFeature,
    PatternFeature,
)
from softwork.core.part import Part
from softwork.core.dependency import DependencyGraph
from softwork.core.selection import SelectionContext
from softwork.core.transaction import AITransaction, HistoryManager, TransactionChange
from softwork.core.document import Document

__all__ = [
    "Parameter",
    "UnitType",
    "Feature",
    "FeatureType",
    "FeatureStatus",
    "BoxFeature",
    "CylinderFeature",
    "MountingPlateFeature",
    "FilletFeature",
    "ChamferFeature",
    "SketchFeature",
    "ExtrudeFeature",
    "RevolveFeature",
    "PatternFeature",
    "Part",
    "DependencyGraph",
    "SelectionContext",
    "AITransaction",
    "HistoryManager",
    "TransactionChange",
    "Document",
]
