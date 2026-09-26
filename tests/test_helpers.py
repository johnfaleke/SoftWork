"""
Test fixture helper utilities for SoftWork test suites.
"""
from __future__ import annotations
from softwork.cad.backend import CADBackend
from softwork.cad.cadquery_backend import CadQueryBackend
from softwork.cad.direct_backend import PrototypeGeometryBackend
from softwork.core.document import Document


def get_test_backend() -> CADBackend:
    """Returns CadQueryBackend if installed/available; otherwise returns PrototypeGeometryBackend for testing."""
    cq = CadQueryBackend()
    if cq.is_cadquery_available:
        return cq
    return PrototypeGeometryBackend()


def create_test_document(name: str = "TestDoc") -> Document:
    """Creates a Document with the test backend."""
    return Document(name=name, backend=get_test_backend())
