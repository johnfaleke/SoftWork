"""
Wavefront OBJ format exporter for SoftWork.
"""
from __future__ import annotations
from softwork.cad.geometry import MeshData


def write_obj_file(mesh: MeshData, filepath: str) -> bool:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# SoftWork Parametric CAD Wavefront OBJ Export\n")
        f.write(f"# Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}\n")
        
        for v in mesh.vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
        for norm in mesh.normals:
            f.write(f"vn {norm[0]:.6f} {norm[1]:.6f} {norm[2]:.6f}\n")
            
        for face in mesh.faces:
            # 1-indexed in OBJ
            f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")
    return True
