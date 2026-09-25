"""
STL format exporter for SoftWork (both ASCII and Binary STL).
"""
from __future__ import annotations
import struct
from softwork.cad.geometry import MeshData


def write_stl_file(mesh: MeshData, filepath: str, binary: bool = True) -> bool:
    if binary:
        return _write_binary_stl(mesh, filepath)
    return _write_ascii_stl(mesh, filepath)


def _write_ascii_stl(mesh: MeshData, filepath: str) -> bool:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("solid SoftWorkModel\n")
        for face in mesh.faces:
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]

            # Calculate face normal (v1-v0) x (v2-v0)
            ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
            length = (nx * nx + ny * ny + nz * nz) ** 0.5
            if length > 0:
                nx, ny, nz = nx / length, ny / length, nz / length
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            f.write(f"  facet normal {nx:.6e} {ny:.6e} {nz:.6e}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n")
            f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
            f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid SoftWorkModel\n")
    return True


def _write_binary_stl(mesh: MeshData, filepath: str) -> bool:
    with open(filepath, "wb") as f:
        # 80-byte header
        header = b"SoftWork AI-native Parametric CAD Binary STL Model" + b" " * 80
        f.write(header[:80])
        # Number of triangles
        f.write(struct.pack("<I", len(mesh.faces)))

        for face in mesh.faces:
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]

            # Normal
            ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
            length = (nx * nx + ny * ny + nz * nz) ** 0.5
            if length > 0:
                nx, ny, nz = nx / length, ny / length, nz / length
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            # 50 bytes per triangle: normal (3 floats), 3 vertices (9 floats), attribute byte count (1 uint16)
            data = struct.pack(
                "<3f3f3f3fH",
                nx, ny, nz,
                v0[0], v0[1], v0[2],
                v1[0], v1[1], v1[2],
                v2[0], v2[1], v2[2],
                0,
            )
            f.write(data)
    return True
