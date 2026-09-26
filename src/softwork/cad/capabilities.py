"""
Backend Capabilities & Diagnostic metadata for SoftWork CAD.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BackendCapabilities:
    """
    Describes the geometric capabilities, authority level, and runtime availability of a CADBackend.
    """
    name: str
    is_available: bool
    is_authoritative_brep: bool
    supports_step: bool
    supports_stl: bool
    diagnostic_message: str = ""
