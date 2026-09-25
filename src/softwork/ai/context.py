"""
Selection and dependency-aware context builder for AI agent reasoning.
"""
from __future__ import annotations
from typing import Dict, Any, List

from softwork.core.document import Document


class AIContextBuilder:
    """
    Constructs compressed, structured context for the AI reasoning pipeline.
    Avoids sending massive raw geometry by summarizing features, parameters, and active selections.
    """

    @staticmethod
    def build_context(document: Document) -> Dict[str, Any]:
        active_part = document.active_part
        selected_feat_id = document.selection.primary_feature_id

        # Features summary
        features_summary = []
        for feat in active_part.features:
            params = {k: f"{v.value}{v.unit}" for k, v in feat.parameters.items()}
            features_summary.append({
                "id": feat.id,
                "name": feat.name,
                "type": feat.feature_type.value,
                "parameters": params,
                "status": feat.status.value,
            })

        # Selected feature context
        selected_info = None
        if selected_feat_id:
            feat = document.get_feature(selected_feat_id)
            if feat:
                selected_info = {
                    "id": feat.id,
                    "name": feat.name,
                    "type": feat.feature_type.value,
                    "parameters": {k: f"{v.value}{v.unit}" for k, v in feat.parameters.items()},
                    "dependencies": feat.dependencies,
                    "dependents": list(document.dependency_graph.get_dependents(feat.id)),
                }

        return {
            "document_name": document.name,
            "part_name": active_part.name,
            "feature_count": len(active_part.features),
            "features": features_summary,
            "selected_feature_id": selected_feat_id,
            "selected_feature": selected_info,
            "has_solid": active_part.active_solid is not None,
            "validation_status": document.latest_validation.is_valid if document.latest_validation else True,
        }
