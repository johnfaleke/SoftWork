"""
Tests for Document core, parameters, dependency graph, and history transactions.
"""
import unittest
from softwork.core.document import Document
from softwork.core.parameter import Parameter
from softwork.core.feature import BoxFeature, MountingPlateFeature
from softwork.commands.parameter_commands import SetParameterCommand


class TestCoreDocument(unittest.TestCase):
    def test_parameter_unit_conversion(self):
        p1 = Parameter(name="width", value=100.0, unit="mm")
        self.assertEqual(p1.canonical_value, 100.0)

        p2 = Parameter.from_string("length", "2.5 in")
        self.assertEqual(p2.unit, "in")
        self.assertAlmostEqual(p2.canonical_value, 63.5, places=2)

        p3 = Parameter.from_string("angle", "90 deg")
        self.assertEqual(p3.unit, "deg")
        self.assertAlmostEqual(p3.canonical_value, 1.570796, places=4)

    def test_document_parametric_recompute(self):
        doc = Document(name="TestDoc")
        plate = MountingPlateFeature(
            length=100.0,
            width=60.0,
            thickness=10.0,
            hole_diameter=8.0,
            hole_offset=10.0,
        )
        doc.add_feature(plate)

        self.assertIsNotNone(doc.active_part.active_solid)
        vol1 = doc.active_part.active_solid.volume

        # Modify parameter via command
        cmd = SetParameterCommand(plate.id, "thickness", 15.0)
        tx = cmd.execute(doc)
        self.assertTrue(tx.is_committed)

        vol2 = doc.active_part.active_solid.volume
        self.assertGreater(vol2, vol1)
        self.assertEqual(doc.get_feature(plate.id).get_parameter("thickness").value, 15.0)

        # Undo
        doc.history.undo()
        doc.recompute()
        self.assertEqual(doc.get_feature(plate.id).get_parameter("thickness").value, 10.0)


if __name__ == "__main__":
    unittest.main()
