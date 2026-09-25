"""
AI Model Provider abstraction for SoftWork.
Decouples agent reasoning from specific LLM vendors (OpenAI, Anthropic, Google, Local, Offline Heuristic).
"""
from __future__ import annotations
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class ProviderResponse:
    content: str
    tool_calls: List[ToolCall]
    raw_response: Optional[Any] = None


class ModelProvider(ABC):
    """
    Abstract AI Model Provider interface.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        tools_schema: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        pass


class HeuristicEngineProvider(ModelProvider):
    """
    Deterministic offline NLP and intent parsing provider.
    Allows zero-latency, private, and testable CAD natural language interpretation.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        tools_schema: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        p_lower = prompt.lower().strip()
        tool_calls: List[ToolCall] = []
        explanation = ""

        # Pattern 1: Create mounting plate / plate
        # "Create a 100 x 60 x 10 mm mounting plate" or "Create 100x60x10 plate"
        plate_match = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*(?:mounting\s+)?plate", p_lower)
        if plate_match:
            l, w, t = float(plate_match.group(1)), float(plate_match.group(2)), float(plate_match.group(3))
            tool_calls.append(
                ToolCall(
                    tool_name="feature.create_plate",
                    arguments={"length": l, "width": w, "thickness": t, "name": "MountingPlate001"},
                )
            )
            explanation = f"I planned and executed the creation of a {l:.0f} × {w:.0f} × {t:.0f} mm parametric mounting plate."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Pattern 2: Create box
        # "Create a 100 x 60 x 10 mm box"
        box_match = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*box", p_lower)
        if box_match:
            w, h, d = float(box_match.group(1)), float(box_match.group(2)), float(box_match.group(3))
            tool_calls.append(
                ToolCall(
                    tool_name="feature.create_box",
                    arguments={"width": w, "height": h, "depth": d, "name": "Box001"},
                )
            )
            explanation = f"I created a {w:.0f} × {h:.0f} × {d:.0f} mm solid box."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Pattern 3: Add holes / M8 holes
        # "Add four M8 holes, 10 mm from each corner"
        hole_match = re.search(r"(?:four|4)\s*(?:m(\d+)|(\d+)\s*mm)?\s*holes?(?:.*?(\d+)\s*mm\s*(?:from|offset))?", p_lower)
        if "hole" in p_lower and hole_match:
            dia = float(hole_match.group(1) or hole_match.group(2) or 8.0)
            offset = float(hole_match.group(3) or 10.0)
            target_feat = (context or {}).get("selected_feature_id") or "MountingPlate001"
            tool_calls.append(
                ToolCall(
                    tool_name="parameter.set",
                    arguments={"feature_id": target_feat, "parameter_name": "hole_diameter", "value": dia},
                )
            )
            tool_calls.append(
                ToolCall(
                    tool_name="parameter.set",
                    arguments={"feature_id": target_feat, "parameter_name": "hole_offset", "value": offset},
                )
            )
            explanation = f"I added four M{dia:.0f} holes with a {offset:.0f} mm corner offset to the plate."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Pattern 4: Fillet outer edges
        # "Fillet the outer edges by 2 mm" or "Add 2 mm fillet"
        fillet_match = re.search(r"fillet.*?(?:by|radius|of)?\s*(\d+(?:\.\d+)?)\s*mm", p_lower) or re.search(r"(\d+(?:\.\d+)?)\s*mm\s*fillet", p_lower)
        if fillet_match:
            radius = float(fillet_match.group(1))
            target_feat = (context or {}).get("selected_feature_id") or "MountingPlate001"
            tool_calls.append(
                ToolCall(
                    tool_name="parameter.set",
                    arguments={"feature_id": target_feat, "parameter_name": "fillet_radius", "value": radius},
                )
            )
            explanation = f"I applied a {radius:.1f} mm fillet to the outer edges."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Pattern 5: Parameter modification (e.g. "Make it 15 mm thick", "Change thickness to 15 mm", "Width to 120")
        thick_match = re.search(r"(?:make (?:it|the plate) |change (?:the )?thickness to )?(\d+(?:\.\d+)?)\s*mm\s*thick", p_lower) or re.search(r"thickness\s*(?:to|=)?\s*(\d+(?:\.\d+)?)", p_lower)
        if thick_match:
            new_val = float(thick_match.group(1))
            target_feat = (context or {}).get("selected_feature_id") or "MountingPlate001"
            tool_calls.append(
                ToolCall(
                    tool_name="parameter.set",
                    arguments={"feature_id": target_feat, "parameter_name": "thickness", "value": new_val},
                )
            )
            explanation = f"I updated the thickness parameter to {new_val:.1f} mm while preserving all holes and fillets."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Pattern 6: Export STEP
        if "export" in p_lower and "step" in p_lower:
            tool_calls.append(
                ToolCall(tool_name="export.step", arguments={"filepath": "model.step"})
            )
            explanation = "I exported the solid geometry to ISO-10303 STEP format."
            return ProviderResponse(content=explanation, tool_calls=tool_calls)

        # Fallback
        explanation = f"I parsed your instruction '{prompt}'. Please verify parameters or select a specific CAD entity."
        return ProviderResponse(content=explanation, tool_calls=tool_calls)
