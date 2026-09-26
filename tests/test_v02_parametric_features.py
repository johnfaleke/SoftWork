"""
Tests for v0.2 parametric features: SketchFeature, ExtrudeFeature, RevolveFeature, PatternFeature, and ChamferFeature.
"""
import unittest
from softwork.core.document import Document
from softwork.core.feature import SketchFeature, ExtrudeFeature, RevolveFeature, PatternFeature, ChamferFeature, BoxFeature
from softwork.commands.feature_commands import (
    CreateSketchCommand,
    ExtrudeSketchCommand,
    RevolveSketchCommand,
    AddPatternCommand,
    AddChamferCommand,
)
from softwork.commands.parameter_commands import SetParameterCommand
from softwork.ai.agent import CADAgent
from tests.test_helpers import create_test_document


class TestV02ParametricFeatures(unittest.TestCase):
    def test_sketch_extrude_workflow(self):
        doc = create_test_document(name="ExtrudeTest")
        # 1. Create sketch with 100x60 rectangle
        sk_feat = SketchFeature(name="Sketch_XY")
        sk_feat.sketch.add_rectangle(100.0, 60.0, centered=True)
        doc.add_feature(sk_feat)

        # 2. Extrude by 25mm
        ext_feat = ExtrudeFeature(target_sketch_feature=sk_feat, distance=25.0, name="Extrude001")
        doc.add_feature(ext_feat)

        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertEqual(doc.active_part.active_solid.volume, 100.0 * 60.0 * 25.0)

        # 3. Parametrically update extrusion distance
        SetParameterCommand(ext_feat.id, "distance", 35.0).execute(doc)
        self.assertEqual(doc.active_part.active_solid.volume, 100.0 * 60.0 * 35.0)

    def test_revolve_feature(self):
        doc = create_test_document(name="RevolveTest")
        sk_feat = SketchFeature(name="Sketch_Revolve")
        sk_feat.sketch.add_rectangle(20.0, 40.0, center_u=30.0, center_v=0.0)
        doc.add_feature(sk_feat)

        rev_feat = RevolveFeature(target_sketch_feature=sk_feat, angle_deg=360.0, axis="Y")
        doc.add_feature(rev_feat)

        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertGreater(doc.active_part.active_solid.volume, 0.0)

    def test_pattern_and_chamfer_features(self):
        doc = create_test_document(name="PatternTest")
        box = BoxFeature(width=20.0, height=20.0, depth=10.0)
        doc.add_feature(box)
        vol_single = doc.active_part.active_solid.volume

        # Linear pattern 3x along X
        pat = PatternFeature(target_feature_id=box.id, count_x=3, count_y=1, spacing_x=30.0)
        doc.add_feature(pat)
        self.assertEqual(doc.active_part.active_solid.volume, vol_single * 3)

        # Add chamfer
        chamf = ChamferFeature(target_feature_id=pat.id, distance=1.0)
        doc.add_feature(chamf)
        self.assertTrue(doc.active_part.active_solid.is_valid)

    def test_ai_agent_sketch_and_extrude_prompt(self):
        doc = create_test_document(name="AIAgentSketchTest")
        agent = CADAgent(doc)

        # Prompt 1: Create sketch
        res1 = agent.execute_prompt("Create sketch on XY plane")
        self.assertTrue(res1.success)
        self.assertEqual(len(doc.active_part.features), 1)

        # Prompt 2: Add rectangle
        res2 = agent.execute_prompt("Add a 100 x 60 mm rectangle to the sketch")
        self.assertTrue(res2.success)

        # Prompt 3: Extrude by 25 mm
        res3 = agent.execute_prompt("Extrude the sketch by 25 mm")
        self.assertTrue(res3.success)
        self.assertEqual(len(doc.active_part.features), 2)
        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertEqual(doc.active_part.active_solid.volume, 100.0 * 60.0 * 25.0)

    def test_sketch_extrude_on_mounting_plate(self):
        doc = create_test_document(name="PlateWithExtrudeBoss")
        agent = CADAgent(doc)

        # 1. Create base mounting plate
        res1 = agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.assertTrue(res1.success)
        base_vol = doc.active_part.active_solid.volume
        self.assertGreater(base_vol, 0.0)

        # 2. Add sketch on plate
        res2 = agent.execute_prompt("Create sketch on XY plane")
        self.assertTrue(res2.success)

        # 3. Add 40x30 mm rectangle boss
        res3 = agent.execute_prompt("Add a 40 x 30 mm rectangle to sketch")
        self.assertTrue(res3.success)

        # 4. Extrude boss by 15 mm
        res4 = agent.execute_prompt("Extrude the sketch by 15 mm")
        self.assertTrue(res4.success)

        # Volume must be base plate volume + boss extrusion volume (40*30*15 = 18000)
        expected_boss_vol = 40.0 * 30.0 * 15.0
        self.assertAlmostEqual(doc.active_part.active_solid.volume, base_vol + expected_boss_vol, delta=1.0)


if __name__ == "__main__":
    unittest.main()
