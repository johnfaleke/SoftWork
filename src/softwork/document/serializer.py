"""
Document serialization and deserialization for native .softwork format.
"""
from __future__ import annotations
import json
from typing import Dict, Any

from softwork.core.document import Document
from softwork.core.feature import (
    BoxFeature,
    CylinderFeature,
    MountingPlateFeature,
    FilletFeature,
    ChamferFeature,
    SketchFeature,
    ExtrudeFeature,
    RevolveFeature,
    HoleWizardFeature,
    ShellFeature,
    PatternFeature,
)
from softwork.core.part import Part
from softwork.sketch.sketch import Sketch


def save_document(document: Document, filepath: str) -> None:
    data = {
        "format": "softwork",
        "schema_version": "0.5.0",
        "document": document.to_dict(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_document(filepath: str, backend: Optional[CADBackend] = None) -> Document:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_data = data["document"]
    doc = Document(name=doc_data.get("name", "Untitled Document"), backend=backend)
    doc.id = doc_data.get("id", doc.id)
    doc.parts.clear()

    for p_data in doc_data.get("parts", []):
        part = Part(id=p_data["id"], name=p_data["name"], color=p_data.get("color", "#3B82F6"))
        for f_data in p_data.get("features", []):
            f_type = f_data["feature_type"]
            params = f_data.get("parameters", {})
            deps = f_data.get("dependencies", [])
            feat = None

            if f_type == "sketch":
                sk_data = f_data.get("sketch_data", {})
                sketch = Sketch.from_dict(sk_data) if sk_data else Sketch(name=f_data["name"])
                feat = SketchFeature(
                    sketch=sketch,
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "extrude":
                target_id = deps[0] if deps else ""
                feat = ExtrudeFeature(
                    target_sketch_feature=target_id,
                    distance=params.get("distance", {}).get("value", 25.0),
                    operation=f_data.get("operation", "add"),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "revolve":
                target_id = deps[0] if deps else ""
                feat = RevolveFeature(
                    target_sketch_feature=target_id,
                    angle_deg=params.get("angle", {}).get("value", 360.0),
                    axis=f_data.get("axis", "Y"),
                    operation=f_data.get("operation", "add"),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "hole_wizard":
                target_id = deps[0] if deps else ""
                feat = HoleWizardFeature(
                    target_feature_id=target_id,
                    metric_size=f_data.get("metric_size", "M8"),
                    hole_type=f_data.get("hole_type", "simple"),
                    depth=params.get("depth", {}).get("value", 20.0),
                    pos_u=params.get("pos_u", {}).get("value", 0.0),
                    pos_v=params.get("pos_v", {}).get("value", 0.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "shell":
                target_id = deps[0] if deps else ""
                feat = ShellFeature(
                    target_feature_id=target_id,
                    wall_thickness=params.get("wall_thickness", {}).get("value", 2.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "pattern":
                target_id = deps[0] if deps else ""
                feat = PatternFeature(
                    target_feature_id=target_id,
                    count_x=int(params.get("count_x", {}).get("value", 2)),
                    count_y=int(params.get("count_y", {}).get("value", 2)),
                    spacing_x=params.get("spacing_x", {}).get("value", 20.0),
                    spacing_y=params.get("spacing_y", {}).get("value", 20.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "fillet":
                target_id = deps[0] if deps else ""
                feat = FilletFeature(
                    target_feature_id=target_id,
                    radius=params.get("radius", {}).get("value", 2.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "chamfer":
                target_id = deps[0] if deps else ""
                feat = ChamferFeature(
                    target_feature_id=target_id,
                    distance=params.get("distance", {}).get("value", 1.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "box":
                feat = BoxFeature(
                    name=f_data["name"],
                    width=params.get("width", {}).get("value", 100.0),
                    height=params.get("height", {}).get("value", 60.0),
                    depth=params.get("depth", {}).get("value", 10.0),
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "cylinder":
                feat = CylinderFeature(
                    name=f_data["name"],
                    radius=params.get("radius", {}).get("value", 10.0),
                    height=params.get("height", {}).get("value", 50.0),
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )
            elif f_type == "mounting_plate":
                feat = MountingPlateFeature(
                    name=f_data["name"],
                    length=params.get("length", {}).get("value", 100.0),
                    width=params.get("width", {}).get("value", 60.0),
                    thickness=params.get("thickness", {}).get("value", 10.0),
                    hole_diameter=params.get("hole_diameter", {}).get("value", 8.0),
                    hole_offset=params.get("hole_offset", {}).get("value", 10.0),
                    fillet_radius=params.get("fillet_radius", {}).get("value", 0.0),
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )

            if feat is not None:
                for p_name, p_dict in params.items():
                    if p_name in feat.parameters and isinstance(p_dict, dict) and "value" in p_dict:
                        feat.parameters[p_name].set_value(p_dict["value"], p_dict.get("unit"))
                part.add_feature(feat)
                doc.dependency_graph.add_node(feat.id)
                for dep in feat.dependencies:
                    doc.dependency_graph.add_dependency(feat.id, dep)

        doc.parts.append(part)

    doc.recompute()
    return doc
