"""
Semantic Topological Reference and Persistent Topology Matching for SoftWork CAD (v0.4).
Solves the CAD topological naming problem by binding geometric entities to semantic intent tags.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import math

from softwork.cad.geometry import Vector3D, Point3D, MeshData


class SemanticRole(Enum):
    TOP_FACE = "face:top"
    BOTTOM_FACE = "face:bottom"
    FRONT_FACE = "face:front"
    BACK_FACE = "face:back"
    LEFT_FACE = "face:left"
    RIGHT_FACE = "face:right"
    HOLE_INNER = "face:hole_inner"
    FILLET_FACE = "face:fillet"
    CHAMFER_FACE = "face:chamfer"
    CYLINDRICAL_FACE = "face:cylinder"
    GENERIC_FACE = "face:generic"


@dataclass
class SemanticReference:
    """
    Persistent semantic identifier for topological entities (faces, edges, vertices).
    Preserves design intent even when underlying geometry indices change during DAG recomputations.
    """
    tag: str
    role: SemanticRole
    parent_feature_id: str
    feature_name: str
    normal_hint: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    centroid_hint: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    area_hint: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def matches_face(self, normal: Tuple[float, float, float], centroid: Tuple[float, float, float], tolerance: float = 0.2) -> float:
        """
        Calculates confidence score [0.0, 1.0] for matching this semantic reference to a face.
        """
        # Normal vector dot product alignment
        dot = (
            self.normal_hint[0] * normal[0] +
            self.normal_hint[1] * normal[1] +
            self.normal_hint[2] * normal[2]
        )
        if dot < 0.7:
            return 0.0

        # Centroid proximity
        dist = math.sqrt(
            (self.centroid_hint[0] - centroid[0]) ** 2 +
            (self.centroid_hint[1] - centroid[1]) ** 2 +
            (self.centroid_hint[2] - centroid[2]) ** 2
        )
        score = max(0.0, 1.0 - (dist / 200.0)) * max(0.0, dot)
        return score


class SemanticTopologyMatcher:
    """
    Analyzes 3D meshes and binds semantic reference tags to geometric faces.
    """

    @staticmethod
    def tag_mesh_faces(mesh: MeshData, feature_id: str = "base", feature_name: str = "BaseFeature") -> List[SemanticReference]:
        """
        Analyzes triangle faces of a mesh and generates semantic reference tags based on normal orientation and bounding box position.
        """
        if not mesh or not mesh.faces or not mesh.vertices:
            return []

        refs: List[SemanticReference] = []

        # Find bounds
        xs = [v[0] for v in mesh.vertices]
        ys = [v[1] for v in mesh.vertices]
        zs = [v[2] for v in mesh.vertices]
        max_z = max(zs) if zs else 0.0
        min_z = min(zs) if zs else 0.0

        for idx, face in enumerate(mesh.faces):
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]

            # Normal calculation
            ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx = ay * bz - az * by
            ny = az * bx - ax * bz
            nz = ax * by - ay * bx
            norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
            if norm_len > 1e-6:
                norm = (nx / norm_len, ny / norm_len, nz / norm_len)
            else:
                norm = (0.0, 0.0, 1.0)

            # Centroid
            cx = (v0[0] + v1[0] + v2[0]) / 3.0
            cy = (v0[1] + v1[1] + v2[1]) / 3.0
            cz = (v0[2] + v1[2] + v2[2]) / 3.0

            # Determine role
            if norm[2] > 0.9 and abs(cz - max_z) < 1.0:
                role = SemanticRole.TOP_FACE
                tag = f"{feature_id}:face:top_{idx}"
            elif norm[2] < -0.9 and abs(cz - min_z) < 1.0:
                role = SemanticRole.BOTTOM_FACE
                tag = f"{feature_id}:face:bottom_{idx}"
            elif norm[1] > 0.9:
                role = SemanticRole.BACK_FACE
                tag = f"{feature_id}:face:back_{idx}"
            elif norm[1] < -0.9:
                role = SemanticRole.FRONT_FACE
                tag = f"{feature_id}:face:front_{idx}"
            elif norm[0] < -0.9:
                role = SemanticRole.LEFT_FACE
                tag = f"{feature_id}:face:left_{idx}"
            elif norm[0] > 0.9:
                role = SemanticRole.RIGHT_FACE
                tag = f"{feature_id}:face:right_{idx}"
            else:
                role = SemanticRole.GENERIC_FACE
                tag = f"{feature_id}:face:generic_{idx}"

            ref = SemanticReference(
                tag=tag,
                role=role,
                parent_feature_id=feature_id,
                feature_name=feature_name,
                normal_hint=norm,
                centroid_hint=(cx, cy, cz),
            )
            refs.append(ref)

        return refs
