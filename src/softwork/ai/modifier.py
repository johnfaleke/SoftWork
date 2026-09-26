"""
AI-Native Parametric Modifier Engine for SoftWork CAD (v0.4).
Parses natural language modification prompts and executes deterministic in-place DAG mutations.
"""
from __future__ import annotations
import re
from typing import Optional, List, Tuple, Dict, Any

from softwork.ai.agent import AgentPlan, AgentExecutionResult
from softwork.commands.parameter_commands import SetParameterCommand, BatchSetParameterCommand
from softwork.core.document import Document
from softwork.core.feature import Feature, MountingPlateFeature, ExtrudeFeature, FilletFeature, HoleWizardFeature, ShellFeature, BoxFeature


class ParametricModifier:
    """
    Analyzes natural language prompts for parametric modifications and targets existing features.
    """

    @staticmethod
    def is_modification_prompt(prompt: str) -> bool:
        """Determines if a prompt is requesting a modification of existing parameters."""
        p = prompt.lower()
        keywords = [
            "make the", "change the", "modify", "increase", "decrease", "resize",
            "set thickness", "set width", "set length", "set height", "set radius",
            "make plate", "make it", "thicker", "wider", "longer", "from m8 to", "from m6 to",
            "change hole", "change fillet", "change chamfer", "change shell", "set material",
        ]
        return any(k in p for k in keywords)

    @classmethod
    def plan_modification(cls, document: Document, prompt: str) -> Optional[AgentPlan]:
        """
        Creates a planned modification with ghost preview mesh without committing to the document.
        """
        p = prompt.lower()
        features = document.active_part.features
        if not features:
            return None

        # 1. Thickness / Extrude Distance Modification
        # e.g. "make the plate 15 mm thick", "make it 20mm thick", "increase thickness to 15"
        m_thick = re.search(r'(?:thickness|thick|height|depth).*?(\d+(?:\.\d+)?)', p) or re.search(r'(\d+(?:\.\d+)?)\s*mm\s*thick', p)
        if m_thick and any(k in p for k in ["make", "change", "set", "increase", "decrease", "modify"]):
            new_val = float(m_thick.group(1))
            # Find target feature
            for feat in reversed(features):
                if isinstance(feat, MountingPlateFeature) and "thickness" in feat.parameters:
                    # Clone & predict ghost
                    ghost_plate = MountingPlateFeature(
                        length=feat.parameters["length"].value,
                        width=feat.parameters["width"].value,
                        thickness=new_val,
                        hole_diameter=feat.parameters["hole_diameter"].value,
                        hole_offset=feat.parameters["hole_offset"].value,
                        fillet_radius=feat.parameters["fillet_radius"].value,
                    )
                    ghost_solid = document.backend.create_plate_with_holes(
                        ghost_plate.parameters["length"].value,
                        ghost_plate.parameters["width"].value,
                        new_val,
                        ghost_plate.parameters["hole_diameter"].value,
                        ghost_plate.parameters["hole_offset"].value,
                        ghost_plate.parameters["fillet_radius"].value,
                    )
                    ghost_mesh = document.backend.to_mesh(ghost_solid)
                    cur_vol = document.active_part.active_solid.volume if document.active_part.active_solid else 0.0
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.thickness to {new_val} mm",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "thickness", "value": new_val}],
                        predicted_delta_vol=ghost_solid.volume - cur_vol,
                        ghost_mesh=ghost_mesh,
                    )
                elif isinstance(feat, ExtrudeFeature) and "distance" in feat.parameters:
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.distance to {new_val} mm",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "distance", "value": new_val}],
                        predicted_delta_vol=0.0,
                    )

        # 2. Hole Size Modification
        # e.g. "change holes to M10", "change the holes from M8 to M10"
        m_hole = re.search(r'(?:to|make)\s*(m\d+)', p)
        if m_hole:
            new_size = m_hole.group(1).upper()
            for feat in reversed(features):
                if isinstance(feat, HoleWizardFeature):
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.metric_size to {new_size}",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "metric_size", "value": new_size}],
                        predicted_delta_vol=0.0,
                    )
                elif isinstance(feat, MountingPlateFeature):
                    # extract diameter from metric
                    d_map = {"M3": 3.4, "M4": 4.5, "M5": 5.5, "M6": 6.6, "M8": 9.0, "M10": 11.0, "M12": 13.5}
                    new_d = d_map.get(new_size, 9.0)
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.hole_diameter to {new_d} mm ({new_size})",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "hole_diameter", "value": new_d}],
                        predicted_delta_vol=0.0,
                    )

        # 3. Fillet Radius Modification
        # e.g. "increase fillet to 4 mm", "change fillet radius to 3"
        m_fillet = re.search(r'(?:fillet).*?(\d+(?:\.\d+)?)', p)
        if m_fillet:
            new_r = float(m_fillet.group(1))
            for feat in reversed(features):
                if isinstance(feat, FilletFeature) and "radius" in feat.parameters:
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.radius to {new_r} mm",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "radius", "value": new_r}],
                        predicted_delta_vol=0.0,
                    )
                elif isinstance(feat, MountingPlateFeature) and "fillet_radius" in feat.parameters:
                    return AgentPlan(
                        prompt=prompt,
                        intent=f"Modify {feat.name}.fillet_radius to {new_r} mm",
                        target_feature_id=feat.id,
                        predicted_tool_calls=[{"tool": "parameter.set", "feature_id": feat.id, "param": "fillet_radius", "value": new_r}],
                        predicted_delta_vol=0.0,
                    )

        # 4. Multi-parameter Dimensions (e.g. "resize width to 80 and length to 120")
        m_w = re.search(r'width\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', p)
        m_l = re.search(r'length\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', p)
        if m_w or m_l:
            mods = []
            for feat in reversed(features):
                if isinstance(feat, MountingPlateFeature) or isinstance(feat, BoxFeature):
                    if m_w and "width" in feat.parameters:
                        mods.append((feat.id, "width", float(m_w.group(1)), "mm"))
                    if m_l and "length" in feat.parameters:
                        mods.append((feat.id, "length", float(m_l.group(1)), "mm"))
                    if mods:
                        return AgentPlan(
                            prompt=prompt,
                            intent=f"Batch modify {feat.name} dimensions",
                            target_feature_id=feat.id,
                            predicted_tool_calls=[{"tool": "parameter.batch_set", "modifications": mods}],
                            predicted_delta_vol=0.0,
                        )

        return None

    @classmethod
    def execute_modification(cls, document: Document, prompt: str) -> Optional[AgentExecutionResult]:
        """
        Executes in-place parametric modification on existing document features.
        """
        p = prompt.lower()
        features = document.active_part.features
        if not features:
            return None

        # 1. Thickness / Extrude Distance
        m_thick = re.search(r'(?:thickness|thick|height|depth).*?(\d+(?:\.\d+)?)', p) or re.search(r'(\d+(?:\.\d+)?)\s*mm\s*thick', p)
        if m_thick and any(k in p for k in ["make", "change", "set", "increase", "decrease", "modify"]):
            new_val = float(m_thick.group(1))
            for feat in reversed(features):
                if isinstance(feat, MountingPlateFeature) and "thickness" in feat.parameters:
                    SetParameterCommand(feat.id, "thickness", new_val).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.thickness to {new_val} mm in parametric history.",
                    )
                elif isinstance(feat, ExtrudeFeature) and "distance" in feat.parameters:
                    SetParameterCommand(feat.id, "distance", new_val).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.distance to {new_val} mm in parametric history.",
                    )

        # 2. Hole Size Modification
        m_hole = re.search(r'(?:to|make)\s*(m\d+)', p)
        if m_hole:
            new_size = m_hole.group(1).upper()
            for feat in reversed(features):
                if isinstance(feat, HoleWizardFeature):
                    SetParameterCommand(feat.id, "metric_size", new_size).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name} to standard {new_size} holes.",
                    )
                elif isinstance(feat, MountingPlateFeature):
                    d_map = {"M3": 3.4, "M4": 4.5, "M5": 5.5, "M6": 6.6, "M8": 9.0, "M10": 11.0, "M12": 13.5}
                    new_d = d_map.get(new_size, 9.0)
                    SetParameterCommand(feat.id, "hole_diameter", new_d).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.hole_diameter to {new_d} mm ({new_size}).",
                    )

        # 3. Fillet Modification
        m_fillet = re.search(r'(?:fillet).*?(\d+(?:\.\d+)?)', p)
        if m_fillet:
            new_r = float(m_fillet.group(1))
            for feat in reversed(features):
                if isinstance(feat, FilletFeature) and "radius" in feat.parameters:
                    SetParameterCommand(feat.id, "radius", new_r).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.radius to {new_r} mm.",
                    )
                elif isinstance(feat, MountingPlateFeature) and "fillet_radius" in feat.parameters:
                    SetParameterCommand(feat.id, "fillet_radius", new_r).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.fillet_radius to {new_r} mm.",
                    )

        # 4. Multi-parameter Dimensions Batch
        m_w = re.search(r'width\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', p)
        m_l = re.search(r'length\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', p)
        if m_w or m_l:
            mods = []
            for feat in reversed(features):
                if isinstance(feat, MountingPlateFeature) or isinstance(feat, BoxFeature):
                    if m_w and "width" in feat.parameters:
                        mods.append((feat.id, "width", float(m_w.group(1)), "mm"))
                    if m_l and "length" in feat.parameters:
                        mods.append((feat.id, "length", float(m_l.group(1)), "mm"))
                    if mods:
                        BatchSetParameterCommand(mods, title=f"Resize {feat.name}").execute(document)
                        return AgentExecutionResult(
                            prompt=prompt,
                            success=True,
                            created_feature_id=feat.id,
                            explanation=f"Batch updated {feat.name} dimensions in a single atomic transaction.",
                        )

        # 5. Shell Wall Thickness
        m_shell = re.search(r'(?:shell|wall).*?(\d+(?:\.\d+)?)', p)
        if m_shell and any(k in p for k in ["make", "change", "set", "increase", "decrease", "modify", "wall"]):
            new_wall = float(m_shell.group(1))
            for feat in reversed(features):
                if isinstance(feat, ShellFeature) and "wall_thickness" in feat.parameters:
                    SetParameterCommand(feat.id, "wall_thickness", new_wall).execute(document)
                    return AgentExecutionResult(
                        prompt=prompt,
                        success=True,
                        created_feature_id=feat.id,
                        explanation=f"Updated {feat.name}.wall_thickness to {new_wall} mm.",
                    )

        return None
