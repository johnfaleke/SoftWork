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


class TestV02ParametricFeatures(unittest.TestCase):
    def test_sketch_extrude_workflow(self):
        doc = Document(name="ExtrudeTest")
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
        doc = Document(name="RevolveTest")
        sk_feat = SketchFeature(name="Sketch_Revolve")
        sk_feat.sketch.add_rectangle(20.0, 40.0, center_u=30.0, center_v=0.0)
        doc.add_feature(sk_feat)

        rev_feat = RevolveFeature(target_sketch_feature=sk_feat, angle_deg=360.0, axis="Y")
        doc.add_feature(rev_feat)

        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertGreater(doc.active_part.active_solid.volume, 0.0)

    def test_pattern_and_chamfer_features(self):
        doc = Document(name="PatternTest")
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
        doc = Document(name="AIAgentSketchTest")
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


if __name__ == "__main__":
    unittest.main()
