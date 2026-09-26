"""
Parametric Document core for SoftWork.
"""
from __future__ import annotations
import uuid
import datetime
from typing import Dict, List, Optional, Any, Callable

from softwork.cad.backend import CADBackend
from softwork.cad.direct_backend import DirectGeometryBackend
from softwork.cad.topology import CADShape
from softwork.cad.validation import GeometryValidator, ValidationReport
from softwork.core.dependency import DependencyGraph
from softwork.core.feature import Feature, FeatureStatus
from softwork.core.material import Material, DEFAULT_MATERIAL
from softwork.core.parameter import Parameter
from softwork.core.part import Part
from softwork.core.selection import SelectionContext
from softwork.core.transaction import HistoryManager, AITransaction


class Document:
    """
    Root CAD document holding the parametric tree, dependency graph,
    history stack, and regeneration pipeline.
    """

    def __init__(self, name: str = "Untitled Document", backend: Optional[CADBackend] = None) -> None:
        self.id: str = f"doc_{uuid.uuid4().hex[:8]}"
        self.name: str = name
        self.created_at: str = datetime.datetime.now().isoformat()
        self.backend: CADBackend = backend or DirectGeometryBackend()
        self.material: Material = DEFAULT_MATERIAL
        
        self.parts: List[Part] = []
        self.global_parameters: Dict[str, Parameter] = {}
        self.dependency_graph: DependencyGraph = DependencyGraph()
        self.history: HistoryManager = HistoryManager()
        self.selection: SelectionContext = SelectionContext()
        self.latest_validation: Optional[ValidationReport] = None
        
        # Listeners for reactive UI updates
        self._change_listeners: List[Callable[[], None]] = []

        # Create default Part001
        default_part = Part(name="Part001")
        self.parts.append(default_part)

    @property
    def active_part(self) -> Part:
        if not self.parts:
            p = Part(name="Part001")
            self.parts.append(p)
        return self.parts[0]

    def add_change_listener(self, listener: Callable[[], None]) -> None:
        self._change_listeners.append(listener)

    def notify_changes(self) -> None:
        for listener in self._change_listeners:
            try:
                listener()
            except Exception:
                pass

    def add_feature(self, feature: Feature, part: Optional[Part] = None) -> None:
        target_part = part or self.active_part
        target_part.add_feature(feature)
        self.dependency_graph.add_node(feature.id)
        for dep in feature.dependencies:
            self.dependency_graph.add_dependency(feature.id, dep)
        self.recompute()

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        for part in self.parts:
            feat = part.get_feature(feature_id)
            if feat is not None:
                return feat
        return None

    def set_parameter(self, feature_id: str, parameter_name: str, value: float, unit: Optional[str] = None) -> None:
        feat = self.get_feature(feature_id)
        if feat is None:
            raise KeyError(f"Feature '{feature_id}' not found")
        feat.set_parameter_value(parameter_name, value, unit)
        self.recompute()

    def recompute(self) -> ValidationReport:
        """
        Recomputes all features in dependency topological order and validates generated geometry.
        Strictly driven by the DependencyGraph DAG:
        1. Syncs all feature dependencies into the DAG.
        2. Resolves topological execution order.
        3. Propagates dirty/failure states down the dependency chain.
        4. Validates each generated shape with GeometryValidator.
        """
        context_shapes: Dict[str, CADShape] = {}
        report = ValidationReport()
        failed_nodes: set[str] = set()

        # 1. Sync DAG nodes and dependency edges from all active features
        all_features: Dict[str, Feature] = {}
        for part in self.parts:
            for feat in part.features:
                all_features[feat.id] = feat
                self.dependency_graph.add_node(feat.id)
                for dep in feat.dependencies:
                    self.dependency_graph.add_dependency(feat.id, dep)

        # 2. Get strict topological evaluation order
        try:
            topo_order = self.dependency_graph.topological_sort()
        except ValueError as e:
            report.add_issue(
                code="CYCLIC_DEPENDENCY",
                message=f"Dependency graph error: {str(e)}",
            )
            self.latest_validation = report
            self.notify_changes()
            return report

        # 3. Evaluate in topological order
        for feat_id in topo_order:
            if feat_id not in all_features:
                continue
            feature = all_features[feat_id]

            if feature.is_suppressed:
                feature.status = FeatureStatus.SUPPRESSED
                continue

            # Check if any parent/dependency failed
            parent_failed = False
            for dep in feature.dependencies:
                if dep in failed_nodes:
                    feature.status = FeatureStatus.FAILED
                    feature.error_message = f"Dependency '{dep}' failed evaluation"
                    failed_nodes.add(feat_id)
                    report.add_issue(
                        code="DEPENDENCY_FAILED",
                        message=f"[{feature.name}] Upstream dependency '{dep}' failed",
                        target_feature_id=feature.id,
                    )
                    parent_failed = True
                    break

            if parent_failed:
                continue

            # Evaluate geometry
            try:
                shape = feature.evaluate(self.backend, context_shapes)
                context_shapes[feature.id] = shape
                feature.status = FeatureStatus.VALID
                feature.error_message = None
                feature.generated_shape = shape

                # Validate individual feature shape
                feat_report = GeometryValidator.validate_shape(shape, feature.id)
                for issue in feat_report.issues:
                    report.add_issue(
                        code=issue.code,
                        message=f"[{feature.name}] {issue.message}",
                        severity=issue.severity,
                        target_feature_id=feature.id,
                        suggested_fix=issue.suggested_fix,
                    )
            except Exception as e:
                feature.status = FeatureStatus.FAILED
                feature.error_message = str(e)
                failed_nodes.add(feat_id)
                report.add_issue(
                    code="FEATURE_EVAL_FAILED",
                    message=f"[{feature.name}] Evaluation failed: {str(e)}",
                    target_feature_id=feature.id,
                )

        # 4. Set active solid for each part to the latest valid solid
        for part in self.parts:
            last_valid_solid = None
            for feat_id in topo_order:
                if feat_id in all_features and any(f.id == feat_id for f in part.features):
                    f = all_features[feat_id]
                    if f.status == FeatureStatus.VALID and f.generated_shape and f.generated_shape.volume > 0:
                        last_valid_solid = f.generated_shape
            part.active_solid = last_valid_solid

        self.latest_validation = report
        self.notify_changes()
        return report

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "parts": [
                {
                    "id": p.id,
                    "name": p.name,
                    "color": p.color,
                    "features": [f.to_dict() for f in p.features],
                }
                for p in self.parts
            ],
            "global_parameters": {k: v.to_dict() for k, v in self.global_parameters.items()},
        }
