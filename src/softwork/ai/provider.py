"""
AI Model Provider abstraction for SoftWork v0.2.
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
    Deterministic offline NLP and intent parsing provider supporting v0.1 & v0.2 workflows.
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

        # 1. Sketch Creation
        # "Create sketch on XY plane" or "New sketch on XZ" or "Sketch on plate"
        sk_match = re.search(r"(?:create|new|add)\s+sketch(?:\s+on\s+(xy|xz|yz|plate|mounting plate|top|face)(?:\s+plane)?)?", p_lower) or re.search(r"^sketch(?:\s+on\s+(xy|xz|yz|plate|top))?", p_lower)
        if sk_match and "extrude" not in p_lower:
            raw_plane = sk_match.group(1) or "xy"
            plane = "XY" if raw_plane in ["plate", "mounting plate", "top", "face"] else raw_plane.upper()
            tool_calls.append(
                ToolCall(tool_name="sketch.create", arguments={"plane": plane, "name": f"Sketch_{plane}"})
            )
            return ProviderResponse(
                content=f"I created a new 2D sketch on the {plane} datum plane.",
                tool_calls=tool_calls,
            )

        # 2. Add Rectangle to Sketch
        # "Add a 100 x 60 mm rectangle"
        sk_rect_match = re.search(r"(?:add\s+)?(?:a\s+)?(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*rectangle", p_lower)
        if sk_rect_match and ("sketch" in p_lower or not context or not context.get("features")):
            w = float(sk_rect_match.group(1))
            h = float(sk_rect_match.group(2))
            tool_calls.append(
                ToolCall(tool_name="sketch.add_rectangle", arguments={"width": w, "height": h, "centered": True})
            )
            return ProviderResponse(
                content=f"I added a centered {w:.0f} × {h:.0f} mm 2D rectangle profile to the active sketch.",
                tool_calls=tool_calls,
            )

        # 3. Add Circle to Sketch
        # "Add a 20 mm circle" or "Circle of radius 15"
        sk_circ_match = re.search(r"(?:add\s+)?(?:a\s+)?(?:r(?:adius)?\s*)?(\d+(?:\.\d+)?)\s*(?:mm)?\s*circle", p_lower)
        if sk_circ_match:
            r = float(sk_circ_match.group(1))
            tool_calls.append(
                ToolCall(tool_name="sketch.add_circle", arguments={"radius": r})
            )
            return ProviderResponse(
                content=f"I added a {r:.1f} mm radius circle profile to the active sketch.",
                tool_calls=tool_calls,
            )

        # 4. Extrude Sketch
        # "Extrude by 25 mm" or "Extrude sketch by 30" or "Extrude on mounting plate"
        ext_match = re.search(r"extrude.*?(?:(?:by|distance|to)\s*)?(\d+(?:\.\d+)?)\s*mm?", p_lower) or (re.search(r"extrude", p_lower) and "revolve" not in p_lower)
        if ext_match:
            if hasattr(ext_match, "group") and ext_match.group(1):
                dist = float(ext_match.group(1))
            else:
                dist = 25.0
            tool_calls.append(
                ToolCall(tool_name="feature.extrude", arguments={"distance": dist, "name": "Extrude001"})
            )
            return ProviderResponse(
                content=f"I extruded the 2D sketch profile by {dist:.1f} mm into a solid body.",
                tool_calls=tool_calls,
            )

        # 5. Revolve Sketch
        # "Revolve by 360 deg" or "Revolve 180 degrees"
        rev_match = re.search(r"revolve.*?(?:by|angle)?\s*(\d+(?:\.\d+)?)\s*(?:deg|degrees)?", p_lower)
        if rev_match:
            ang = float(rev_match.group(1))
            tool_calls.append(
                ToolCall(tool_name="feature.revolve", arguments={"angle_deg": ang, "axis": "Y", "name": "Revolve001"})
            )
            return ProviderResponse(
                content=f"I revolved the 2D sketch profile by {ang:.0f} degrees around the vertical axis.",
                tool_calls=tool_calls,
            )

        # 6. Pattern
        # "Pattern 3 times along X" or "Pattern count 4"
        pat_match = re.search(r"pattern.*?(\d+)\s*(?:times|count)?", p_lower)
        if pat_match:
            cnt = int(pat_match.group(1))
            target_feat = (context or {}).get("selected_feature_id") or "Extrude001"
            tool_calls.append(
                ToolCall(tool_name="feature.pattern", arguments={"target_feature_id": target_feat, "count_x": cnt, "spacing_x": 30.0})
            )
            return ProviderResponse(
                content=f"I created a linear pattern array with {cnt} instances.",
                tool_calls=tool_calls,
            )

        # 7. Chamfer
        # "Chamfer 1 mm" or "Chamfer edges by 2 mm"
        chamf_match = re.search(r"chamfer.*?(?:by|of)?\s*(\d+(?:\.\d+)?)\s*mm?", p_lower)
        if chamf_match:
            dist = float(chamf_match.group(1))
            target_feat = (context or {}).get("selected_feature_id") or "MountingPlate001"
            tool_calls.append(
                ToolCall(tool_name="feature.chamfer", arguments={"target_feature_id": target_feat, "distance": dist})
            )
            return ProviderResponse(
                content=f"I applied a {dist:.1f} mm chamfer to the outer edges.",
                tool_calls=tool_calls,
            )

        # 8. Create mounting plate
        plate_match = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*(?:mounting\s+)?plate", p_lower)
        if plate_match:
            l, w, t = float(plate_match.group(1)), float(plate_match.group(2)), float(plate_match.group(3))
            tool_calls.append(
                ToolCall(
                    tool_name="feature.create_plate",
                    arguments={"length": l, "width": w, "thickness": t, "name": "MountingPlate001"},
                )
            )
            return ProviderResponse(
                content=f"I planned and executed the creation of a {l:.0f} × {w:.0f} × {t:.0f} mm parametric mounting plate.",
                tool_calls=tool_calls,
            )

        # 9. Create box
        box_match = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*box", p_lower)
        if box_match:
            w, h, d = float(box_match.group(1)), float(box_match.group(2)), float(box_match.group(3))
            tool_calls.append(
                ToolCall(
                    tool_name="feature.create_box",
                    arguments={"width": w, "height": h, "depth": d, "name": "Box001"},
                )
            )
            return ProviderResponse(
                content=f"I created a {w:.0f} × {h:.0f} × {d:.0f} mm solid box.",
                tool_calls=tool_calls,
            )

        # 10. Add holes / M8 holes
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
            return ProviderResponse(
                content=f"I added four M{dia:.0f} holes with a {offset:.0f} mm corner offset to the plate.",
                tool_calls=tool_calls,
            )

        # 11. Fillet
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
            return ProviderResponse(
                content=f"I applied a {radius:.1f} mm fillet to the outer edges.",
                tool_calls=tool_calls,
            )

        # 12. Parameter change (e.g. thickness)
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
            return ProviderResponse(
                content=f"I updated the thickness parameter to {new_val:.1f} mm while preserving all holes and fillets.",
                tool_calls=tool_calls,
            )

        # 13. Export STEP
        if "export" in p_lower and "step" in p_lower:
            tool_calls.append(
                ToolCall(tool_name="export.step", arguments={"filepath": "model.step"})
            )
            return ProviderResponse(
                content="I exported the solid geometry to ISO-10303 STEP format.",
                tool_calls=tool_calls,
            )

        return ProviderResponse(
            content=f"I received instruction '{prompt}'. Please verify parameters or select a target feature.",
            tool_calls=tool_calls,
        )
