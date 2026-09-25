"""
Document serialization and deserialization for native .softwork format.
"""
from __future__ import annotations
import json
from typing import Dict, Any

from softwork.core.document import Document
from softwork.core.feature import BoxFeature, CylinderFeature, MountingPlateFeature, FilletFeature
from softwork.core.part import Part


def save_document(document: Document, filepath: str) -> None:
    data = {
        "format": "softwork",
        "schema_version": "0.1.0",
        "document": document.to_dict(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_document(filepath: str) -> Document:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_data = data["document"]
    doc = Document(name=doc_data.get("name", "Untitled Document"))
    doc.id = doc_data.get("id", doc.id)
    doc.parts.clear()

    for p_data in doc_data.get("parts", []):
        part = Part(id=p_data["id"], name=p_data["name"], color=p_data.get("color", "#3B82F6"))
        for f_data in p_data.get("features", []):
            f_type = f_data["feature_type"]
            params = f_data.get("parameters", {})
            feat = None

            if f_type == "box":
                feat = BoxFeature(
                    name=f_data["name"],
                    width=params.get("width", {}).get("value", 100.0),
                    height=params.get("height", {}).get("value", 60.0),
                    depth=params.get("depth", {}).get("value", 10.0),
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
            elif f_type == "fillet":
                deps = f_data.get("dependencies", [])
                target_id = deps[0] if deps else ""
                feat = FilletFeature(
                    target_feature_id=target_id,
                    radius=params.get("radius", {}).get("value", 2.0),
                    name=f_data["name"],
                    id=f_data["id"],
                    provenance=f_data.get("provenance", "user"),
                )

            if feat is not None:
                doc.add_feature(feat, part)

        doc.parts.append(part)

    doc.recompute()
    return doc
