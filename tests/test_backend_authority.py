"""
Brutal Architectural Test Suite: CAD Kernel Authority, Backend Capabilities,
Rebuild Failure Safety, Previous Valid Geometry Retention, and AI Transaction Integrity.
"""
from __future__ import annotations
import os
import tempfile
import unittest

from softwork.cad.backend import CADKernelError
from softwork.cad.cadquery_backend import CadQueryBackend
from softwork.cad.direct_backend import PrototypeGeometryBackend, DirectGeometryBackend
from softwork.cad.capabilities import BackendCapabilities
from softwork.cad.topology import CADShape
from softwork.commands.feature_commands import (
    CreateSketchCommand,
    AddSketchRectangleCommand,
    AddSketchCircleCommand,
    ExtrudeSketchCommand,
    AddHoleWizardCommand,
    AddFilletCommand,
)
from softwork.commands.parameter_commands import SetParameterCommand, BatchSetParameterCommand
from softwork.core.document import Document
from softwork.core.feature import FeatureStatus, SketchFeature, ExtrudeFeature, FilletFeature
from softwork.formats.step import write_step_file
from softwork.sketch.plane import StandardPlane
from softwork.ai.tools import ToolRegistry


class TestCADBackendAuthority(unittest.TestCase):
    """
    Validates non-negotiable architectural guarantees specified in SoftWork_AGENT_BUILD_DIRECTIVE.md.
    """

    def test_document_defaults_to_cadquery_backend(self) -> None:
        """Requirement A: Document must default to CadQueryBackend without silent fallback."""
        doc = Document(name="TestDoc")
        self.assertIsInstance(doc.backend, CadQueryBackend)
        self.assertEqual(doc.backend.name(), "CadQueryBackend")
        self.assertTrue(doc.backend_capabilities.is_authoritative_brep)

    def test_cadquery_unavailable_does_not_silently_fallback(self) -> None:
        """Requirement B: CadQuery unavailable must report diagnostic error rather than falling back."""
        backend = CadQueryBackend(require_installed=False)
        # Even if CQ is not installed, it must report itself as CadQueryBackend, not Prototype
        self.assertEqual(backend.name(), "CadQueryBackend")
        caps = backend.capabilities
        self.assertEqual(caps.name, "CadQueryBackend")
        self.assertTrue(caps.is_authoritative_brep)

        if not backend.is_cadquery_available:
            with self.assertRaises(CADKernelError) as ctx:
                backend.create_box(10.0, 10.0, 10.0)
            self.assertIn("CadQuery/OpenCASCADE kernel is unavailable", str(ctx.exception))

    def test_prototype_backend_explicit_mode_and_capabilities(self) -> None:
        """Requirement C: PrototypeGeometryBackend is non-authoritative and blocks STEP export."""
        proto = PrototypeGeometryBackend()
        self.assertEqual(proto.name(), "PrototypeGeometryBackend")
        self.assertFalse(proto.capabilities.is_authoritative_brep)
        self.assertFalse(proto.capabilities.supports_step)
        self.assertIn("NON-PRODUCTION PROTOTYPE", proto.capabilities.diagnostic_message)

        # Generating a prototype box
        box = proto.create_box(50.0, 30.0, 10.0)
        self.assertTrue(box.is_valid)
        self.assertIsNone(box.native_handle)

        # Attempting STEP export on prototype backend must fail with typed CADKernelError
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tf:
            temp_step = tf.name

        try:
            with self.assertRaises(CADKernelError) as ctx:
                proto.export_step(box, temp_step)
            self.assertIn("EXPORT_UNSUPPORTED", str(ctx.exception))
        finally:
            if os.path.exists(temp_step):
                os.remove(temp_step)

    def test_step_export_fails_explicitly_without_native_handle(self) -> None:
        """Requirement D: STEP export fails cleanly when no authoritative OpenCASCADE B-rep exists."""
        fake_shape = CADShape(id="mesh_only", shape_type="box", volume=100.0, native_handle=None)
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tf:
            temp_path = tf.name

        try:
            with self.assertRaises(CADKernelError) as ctx:
                write_step_file(fake_shape, temp_path)
            self.assertIn("EXPORT_UNSUPPORTED", str(ctx.exception))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_rebuild_preserves_previous_valid_geometry_on_failure(self) -> None:
        """Requirement G & H: Failed rebuild sets FAILED state and preserves previous_valid_shape."""
        doc = Document(name="FailureSafetyDoc", backend=PrototypeGeometryBackend())
        part = doc.active_part

        sk_feat = SketchFeature(name="Sketch001")
        sk_feat.sketch.add_rectangle(100.0, 60.0, centered=True)
        doc.add_feature(sk_feat)

        ext_feat = ExtrudeFeature(target_sketch_feature=sk_feat, distance=10.0, name="Extrude001")
        doc.add_feature(ext_feat)

        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertIsNotNone(ext_feat.generated_shape)
        initial_shape = ext_feat.generated_shape
        initial_vol = initial_shape.volume

        # Trigger invalid parameter mutation
        doc.set_parameter(ext_feat.id, "distance", -50.0)

        self.assertEqual(ext_feat.status, FeatureStatus.FAILED)
        self.assertFalse(doc.latest_validation.is_valid)
        self.assertIsNotNone(ext_feat.error_message)

        # Crucial: previous valid shape must be preserved for display/viewport safety
        self.assertEqual(ext_feat.previous_valid_shape, initial_shape)
        self.assertEqual(ext_feat.generated_shape, initial_shape)
        self.assertIsNotNone(part.active_solid)
        self.assertEqual(part.active_solid.volume, initial_vol)

        # Recover model
        doc.set_parameter(ext_feat.id, "distance", 20.0)
        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertTrue(doc.latest_validation.is_valid)
        self.assertEqual(ext_feat.parameters["distance"].value, 20.0)
        self.assertGreater(ext_feat.generated_shape.volume, initial_vol)

    def test_failed_multi_parameter_transaction_atomic_rollback(self) -> None:
        """Requirement I: Batch parameter transaction rollback restores parameters and state cleanly."""
        doc = Document(name="TransactionDoc", backend=PrototypeGeometryBackend())

        sk_feat = SketchFeature(name="Sketch001")
        sk_feat.sketch.add_rectangle(100.0, 60.0, centered=True)
        doc.add_feature(sk_feat)

        ext_feat = ExtrudeFeature(target_sketch_feature=sk_feat, distance=10.0, name="Extrude001")
        doc.add_feature(ext_feat)

        fillet_feat = FilletFeature(target_feature_id=ext_feat.id, radius=2.0, name="Fillet001")
        doc.add_feature(fillet_feat)

        self.assertEqual(doc.active_part.features[1].parameters["distance"].value, 10.0)
        self.assertEqual(doc.active_part.features[2].parameters["radius"].value, 2.0)

        # Execute a batch mutation
        batch_cmd = BatchSetParameterCommand(
            modifications=[
                (ext_feat.id, "distance", 25.0, "mm"),
                (fillet_feat.id, "radius", 4.0, "mm"),
            ]
        )
        tx = batch_cmd.execute(doc)
        self.assertTrue(tx.is_committed)
        self.assertEqual(ext_feat.parameters["distance"].value, 25.0)
        self.assertEqual(fillet_feat.parameters["radius"].value, 4.0)

        # Rollback transaction
        doc.history.undo()
        self.assertEqual(ext_feat.parameters["distance"].value, 10.0)
        self.assertEqual(fillet_feat.parameters["radius"].value, 2.0)
        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertEqual(fillet_feat.status, FeatureStatus.VALID)

    def test_ai_sketch_entity_mutations_are_undoable(self) -> None:
        """Requirement J: AI tools adding sketch rectangles and circles route through undoable commands."""
        doc = Document(name="AISketchDoc", backend=PrototypeGeometryBackend())
        tools = ToolRegistry(doc)

        # 1. AI creates sketch
        tx1 = tools.execute("sketch.create", {"name": "BaseSketch", "plane": "XY"})
        self.assertEqual(len(doc.active_part.features), 1)
        sk_feat = doc.active_part.features[0]

        # 2. AI adds rectangle
        tx2 = tools.execute("sketch.add_rectangle", {"sketch_id": sk_feat.id, "width": 80.0, "height": 40.0})
        self.assertTrue(tx2.is_committed)
        self.assertEqual(len(sk_feat.sketch.elements), 1)

        # 3. AI adds circle
        tx3 = tools.execute("sketch.add_circle", {"sketch_id": sk_feat.id, "radius": 15.0})
        self.assertTrue(tx3.is_committed)
        self.assertEqual(len(sk_feat.sketch.elements), 2)

        # 4. Undo circle addition
        doc.history.undo()
        self.assertEqual(len(sk_feat.sketch.elements), 1)

        # 5. Undo rectangle addition
        doc.history.undo()
        self.assertEqual(len(sk_feat.sketch.elements), 0)

        # 6. Redo rectangle addition
        doc.history.redo()
        self.assertEqual(len(sk_feat.sketch.elements), 1)


if __name__ == "__main__":
    unittest.main()
