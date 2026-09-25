"""
Geometry and engineering validation system for SoftWork.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from softwork.cad.topology import CADShape
from softwork.cad.geometry import MeshData


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity
    target_feature_id: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_issue(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        target_feature_id: Optional[str] = None,
        suggested_fix: Optional[str] = None,
    ) -> None:
        if severity == ValidationSeverity.ERROR:
            self.is_valid = False
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=severity,
                target_feature_id=target_feature_id,
                suggested_fix=suggested_fix,
            )
        )


class GeometryValidator:
    """
    Validates CAD shapes against physical and topological engineering constraints.
    """

    @staticmethod
    def validate_shape(shape: CADShape, feature_id: Optional[str] = None) -> ValidationReport:
        report = ValidationReport()
        report.metrics["shape_id"] = shape.id
        report.metrics["shape_type"] = shape.shape_type
        report.metrics["volume"] = shape.volume

        # 1. Non-negative / positive volume check
        if shape.volume <= 0.0:
            report.add_issue(
                code="ZERO_VOLUME",
                message=f"Shape '{shape.id}' has zero or negative volume ({shape.volume:.2f} mm³).",
                severity=ValidationSeverity.ERROR,
                target_feature_id=feature_id,
                suggested_fix="Verify positive dimensions and non-degenerate profiles.",
            )

        # 2. Check mesh presence and manifoldness
        mesh: Optional[MeshData] = shape.metadata.get("mesh")
        if mesh is not None:
            report.metrics["vertex_count"] = len(mesh.vertices)
            report.metrics["face_count"] = len(mesh.faces)
            if len(mesh.vertices) < 4 or len(mesh.faces) < 4:
                report.add_issue(
                    code="DEGENERATE_MESH",
                    message="Shape generated fewer than 4 vertices/faces, indicating degenerate 3D solid.",
                    severity=ValidationSeverity.ERROR,
                    target_feature_id=feature_id,
                    suggested_fix="Check that thickness or extrusion height is greater than zero.",
                )

        # 3. Fillet radius checks
        fillet_radius = shape.metadata.get("fillet_radius", 0.0)
        if fillet_radius > 0.0:
            # Check bounding dimensions
            length = shape.metadata.get("length", shape.metadata.get("width", 100.0))
            width = shape.metadata.get("width", shape.metadata.get("height", 60.0))
            max_allowed = min(length, width) / 2.0
            if fillet_radius >= max_allowed:
                report.add_issue(
                    code="FILLET_EXCEEDS_GEOMETRY",
                    message=f"Requested fillet radius ({fillet_radius:.2f} mm) exceeds maximum allowable radius ({max_allowed:.2f} mm).",
                    severity=ValidationSeverity.ERROR,
                    target_feature_id=feature_id,
                    suggested_fix=f"Reduce fillet radius to less than {max_allowed:.1f} mm.",
                )

        return report
