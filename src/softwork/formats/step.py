"""
STEP (ISO 10303-21) exporter for SoftWork.
Requires authoritative OpenCASCADE B-rep geometry.
"""
from __future__ import annotations
import os
from softwork.cad.backend import CADKernelError
from softwork.cad.topology import CADShape


def write_step_file(shape: CADShape, filepath: str) -> bool:
    """
    Exports genuine OpenCASCADE B-rep shape to ISO-10303 STEP format.
    Raises CADKernelError if shape lacks a native OpenCASCADE B-rep handle.
    """
    if shape.native_handle is None:
        raise CADKernelError(
            "EXPORT_UNSUPPORTED: Cannot export shape to STEP. "
            "Authoritative OpenCASCADE B-rep geometry handle is missing."
        )
    try:
        import cadquery as cq
        cq.exporters.export(shape.native_handle, filepath, "STEP")
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            raise CADKernelError(f"STEP export failed to write valid output file to {filepath}")
        return True
    except ImportError as e:
        raise CADKernelError(
            "CadQuery/OpenCASCADE is required for STEP export. "
            "Install CadQuery in your environment."
        ) from e
    except Exception as e:
        raise CADKernelError(f"STEP export failed: {str(e)}") from e

