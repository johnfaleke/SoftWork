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

    def test_material_and_mass_properties(self):
        doc = Document(name="MaterialDoc")
        plate = MountingPlateFeature(length=100.0, width=60.0, thickness=10.0, hole_diameter=0.0)
        doc.add_feature(plate)

        vol = doc.active_part.active_solid.volume
        self.assertAlmostEqual(vol, 60000.0, places=1)

        # Aluminum 6061-T6 density: 2.70 g/cm3 -> Mass = 60 cm3 * 2.7 = 162 g
        mass_al = doc.material.calculate_mass_grams(vol)
        self.assertAlmostEqual(mass_al, 162.0, places=1)

        # Switch to Steel 1018 (7.85 g/cm3)
        from softwork.core.material import STANDARD_MATERIALS
        doc.material = STANDARD_MATERIALS["Plain Carbon Steel 1018"]
        mass_steel = doc.material.calculate_mass_grams(vol)
        self.assertAlmostEqual(mass_steel, 471.0, places=1)


if __name__ == "__main__":
    unittest.main()
