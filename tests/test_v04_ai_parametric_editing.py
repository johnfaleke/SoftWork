"""
Unit tests for Milestone v0.4: AI-Native Parametric Editing & Semantic Topological References.
"""
from __future__ import annotations
import unittest

from softwork.ai.agent import CADAgent
from softwork.core.document import Document
from softwork.core.feature import MountingPlateFeature, ExtrudeFeature
from softwork.core.semantic import SemanticTopologyMatcher, SemanticRole, SemanticReference
from softwork.commands.feature_commands import CreateMountingPlateCommand, CreateSketchCommand, ExtrudeSketchCommand


class TestV04AIParametricEditing(unittest.TestCase):
    """
    Validates in-place parametric modification, multi-parameter batch mutations,
    semantic topological tagging, and DAG preservation for Milestone v0.4.
    """

    def test_nlp_in_place_thickness_modification(self) -> None:
        doc = Document(name="PlateWorkflow.softwork")
        agent = CADAgent(doc)

        # 1. Create initial mounting plate
        res1 = agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.assertTrue(res1.success)
        self.assertEqual(len(doc.active_part.features), 1)
        plate = doc.active_part.features[0]
        self.assertAlmostEqual(plate.parameters["thickness"].value, 10.0)

        # 2. Add holes
        res2 = agent.execute_prompt("Add four M8 holes, 10 mm from each corner")
        self.assertTrue(res2.success)

        # 3. Modify thickness in-place (Core SoftWork thesis test)
        plan = agent.plan_prompt("Make the plate 15 mm thick")
        self.assertIsNotNone(plan)
        self.assertIn("15", plan.intent)

        res3 = agent.execute_prompt("Make the plate 15 mm thick")
        self.assertTrue(res3.success)
        # Should NOT have created a duplicate feature; should have modified plate in-place
        self.assertAlmostEqual(plate.parameters["thickness"].value, 15.0)
        self.assertIn("thickness", res3.explanation.lower())

    def test_nlp_hole_and_fillet_modifications(self) -> None:
        doc = Document(name="HoleFillet.softwork")
        agent = CADAgent(doc)

        CreateMountingPlateCommand(length=100.0, width=60.0, thickness=10.0, hole_diameter=8.0, fillet_radius=2.0).execute(doc)
        plate = doc.active_part.features[0]

        # Change holes to M10
        res1 = agent.execute_prompt("Change the holes to M10")
        self.assertTrue(res1.success)
        self.assertAlmostEqual(plate.parameters["hole_diameter"].value, 11.0)

        # Change fillet to 4mm
        res2 = agent.execute_prompt("Increase fillet to 4 mm")
        self.assertTrue(res2.success)
        self.assertAlmostEqual(plate.parameters["fillet_radius"].value, 4.0)

    def test_batch_dimension_modification(self) -> None:
        doc = Document(name="BatchDim.softwork")
        agent = CADAgent(doc)

        CreateMountingPlateCommand(length=100.0, width=60.0, thickness=10.0).execute(doc)
        plate = doc.active_part.features[0]

        res = agent.execute_prompt("Resize width to 80 and length to 120")
        self.assertTrue(res.success)
        self.assertAlmostEqual(plate.parameters["width"].value, 80.0)
        self.assertAlmostEqual(plate.parameters["length"].value, 120.0)

    def test_semantic_reference_tagging_and_matching(self) -> None:
        doc = Document(name="SemanticDoc.softwork")
        CreateMountingPlateCommand(length=100.0, width=60.0, thickness=10.0).execute(doc)

        solid = doc.active_part.active_solid
        self.assertIsNotNone(solid)
        mesh = doc.backend.to_mesh(solid)
        self.assertIsNotNone(mesh)

        # Tag faces
        refs = SemanticTopologyMatcher.tag_mesh_faces(mesh, feature_id="feat_01", feature_name="MountingPlate")
        self.assertGreater(len(refs), 0)

        # Verify presence of standard topological roles
        roles = {r.role for r in refs}
        self.assertIn(SemanticRole.TOP_FACE, roles)
        self.assertIn(SemanticRole.BOTTOM_FACE, roles)

        # Test matching against known top face
        top_ref = [r for r in refs if r.role == SemanticRole.TOP_FACE][0]
        score = top_ref.matches_face(normal=(0.0, 0.0, 1.0), centroid=top_ref.centroid_hint)
        self.assertGreater(score, 0.8)


if __name__ == "__main__":
    unittest.main()
