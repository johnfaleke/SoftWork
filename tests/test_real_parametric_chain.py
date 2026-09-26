"""
Brutal Integration Test: Real Parametric Feature Chain DAG Recomputation Engine.
Tests full parametric dependency chain (Sketch -> Extrude -> Hole -> Pattern -> Fillet),
parameter mutations, failure propagation, model recovery, and serialization.
"""
from __future__ import annotations
import os
import tempfile
import unittest

from softwork.core.document import Document
from softwork.core.feature import (
    FeatureStatus,
    SketchFeature,
    ExtrudeFeature,
    HoleWizardFeature,
    PatternFeature,
    FilletFeature,
)
from softwork.document.serializer import save_document, load_document
from softwork.sketch.plane import SketchPlane, StandardPlane


class TestRealParametricChain(unittest.TestCase):
    """
    Validates end-to-end parametric graph recomputation on a multi-feature CAD chain.
    """

    def test_canonical_parametric_chain_lifecycle(self) -> None:
        doc = Document(name="BracketPart")
        part = doc.active_part

        # 1. Sketch001: 100 x 60 mm rectangle on XY plane
        sk_feat = SketchFeature(name="Sketch001")
        sk_feat.sketch.plane = SketchPlane(StandardPlane.XY)
        sk_feat.sketch.add_rectangle(width=100.0, height=60.0, centered=True)
        doc.add_feature(sk_feat)

        # 2. Extrude001: 10 mm extrusion depending on Sketch001
        ext_feat = ExtrudeFeature(
            target_sketch_feature=sk_feat,
            distance=10.0,
            name="Extrude001",
        )
        doc.add_feature(ext_feat)

        # 3. Hole001: M8 Hole Wizard depending on Extrude001
        hole_feat = HoleWizardFeature(
            target_feature_id=ext_feat.id,
            metric_size="M8",
            hole_type="counterbore",
            depth=15.0,
            pos_u=0.0,
            pos_v=0.0,
            name="Hole001",
        )
        doc.add_feature(hole_feat)

        # 4. Pattern001: Linear pattern depending on Hole001
        pat_feat = PatternFeature(
            target_feature_id=hole_feat.id,
            count_x=2,
            count_y=2,
            spacing_x=30.0,
            spacing_y=20.0,
            name="Pattern001",
        )
        doc.add_feature(pat_feat)

        # 5. Fillet001: 2 mm fillet depending on Pattern001
        fillet_feat = FilletFeature(
            target_feature_id=pat_feat.id,
            radius=2.0,
            name="Fillet001",
        )
        doc.add_feature(fillet_feat)

        # Verify initial rebuild
        self.assertEqual(len(part.features), 5)
        self.assertTrue(doc.latest_validation.is_valid)
        self.assertEqual(sk_feat.status, FeatureStatus.VALID)
        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertEqual(hole_feat.status, FeatureStatus.VALID)
        self.assertEqual(pat_feat.status, FeatureStatus.VALID)
        self.assertEqual(fillet_feat.status, FeatureStatus.VALID)
        self.assertIsNotNone(part.active_solid)

        initial_vol = part.active_solid.volume
        self.assertGreater(initial_vol, 0.0)

        # -------------------------------------------------------------
        # Step 2: Mutate Extrude001 distance = 15.0 mm
        # -------------------------------------------------------------
        doc.set_parameter(ext_feat.id, "distance", 15.0)

        # Verify all features recomputed successfully
        self.assertEqual(ext_feat.parameters["distance"].value, 15.0)
        self.assertEqual(sk_feat.status, FeatureStatus.VALID)
        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertEqual(hole_feat.status, FeatureStatus.VALID)
        self.assertEqual(pat_feat.status, FeatureStatus.VALID)
        self.assertEqual(fillet_feat.status, FeatureStatus.VALID)
        self.assertTrue(doc.latest_validation.is_valid)
        self.assertGreater(part.active_solid.volume, initial_vol)

        # -------------------------------------------------------------
        # Step 3: Mutate Extrude001 distance = -100.0 mm (Invalid parameter)
        # -------------------------------------------------------------
        doc.set_parameter(ext_feat.id, "distance", -100.0)

        # Recompute must catch failure, mark Extrude001 and all downstream features as FAILED
        self.assertFalse(doc.latest_validation.is_valid)
        self.assertEqual(ext_feat.status, FeatureStatus.FAILED)
        self.assertIn("Extrude distance must be strictly positive", ext_feat.error_message)

        # Downstream features must be flagged as FAILED due to broken dependency
        self.assertEqual(hole_feat.status, FeatureStatus.FAILED)
        self.assertEqual(pat_feat.status, FeatureStatus.FAILED)
        self.assertEqual(fillet_feat.status, FeatureStatus.FAILED)

        # -------------------------------------------------------------
        # Step 4: Recover model by restoring valid parameter (15.0 mm)
        # -------------------------------------------------------------
        doc.set_parameter(ext_feat.id, "distance", 15.0)

        self.assertTrue(doc.latest_validation.is_valid)
        self.assertEqual(ext_feat.status, FeatureStatus.VALID)
        self.assertIsNone(ext_feat.error_message)
        self.assertEqual(hole_feat.status, FeatureStatus.VALID)
        self.assertEqual(pat_feat.status, FeatureStatus.VALID)
        self.assertEqual(fillet_feat.status, FeatureStatus.VALID)
        self.assertIsNotNone(part.active_solid)

        # -------------------------------------------------------------
        # Step 5: Save, close, reopen, and rebuild
        # -------------------------------------------------------------
        with tempfile.NamedTemporaryFile(suffix=".softwork", delete=False) as tf:
            temp_path = tf.name

        try:
            save_document(doc, temp_path)
            loaded_doc = load_document(temp_path)

            self.assertEqual(len(loaded_doc.active_part.features), 5)
            loaded_ext = loaded_doc.get_feature(ext_feat.id)
            self.assertIsNotNone(loaded_ext)
            self.assertEqual(loaded_ext.parameters["distance"].value, 15.0)

            # Rebuild loaded doc
            report = loaded_doc.recompute()
            self.assertTrue(report.is_valid)
            self.assertEqual(len(report.issues), 0)
            self.assertAlmostEqual(loaded_doc.active_part.active_solid.volume, doc.active_part.active_solid.volume, places=1)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
