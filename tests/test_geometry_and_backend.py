"""
Tests for CAD geometry, backend abstraction, and validation.
"""
import unittest
from softwork.cad.direct_backend import DirectGeometryBackend
from softwork.cad.cadquery_backend import CadQueryBackend
from softwork.cad.validation import GeometryValidator, ValidationSeverity


class TestGeometryAndBackend(unittest.TestCase):
    def test_create_box(self):
        backend = DirectGeometryBackend()
        box = backend.create_box(100.0, 60.0, 10.0, center=True)
        self.assertTrue(box.is_valid)
        self.assertEqual(box.volume, 60000.0)
        self.assertEqual(box.shape_type, "box")

        mesh = backend.to_mesh(box)
        self.assertEqual(len(mesh.vertices), 8)
        self.assertEqual(len(mesh.faces), 12)

        report = GeometryValidator.validate_shape(box)
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.issues), 0)

    def test_create_mounting_plate_with_holes(self):
        backend = DirectGeometryBackend()
        plate = backend.create_plate_with_holes(
            length=100.0,
            width=60.0,
            thickness=10.0,
            hole_diameter=8.0,
            hole_offset=10.0,
            fillet_radius=2.0,
        )
        self.assertTrue(plate.is_valid)
        self.assertGreater(plate.volume, 0.0)
        mesh = backend.to_mesh(plate)
        self.assertGreater(len(mesh.vertices), 20)
        self.assertGreater(len(mesh.faces), 20)

        report = GeometryValidator.validate_shape(plate)
        self.assertTrue(report.is_valid)

    def test_fillet_validation(self):
        backend = DirectGeometryBackend()
        # Try invalid large fillet
        plate = backend.create_plate_with_holes(
            length=50.0,
            width=30.0,
            thickness=5.0,
            hole_diameter=4.0,
            hole_offset=5.0,
            fillet_radius=25.0,  # exceeds half width (15mm)
        )
        report = GeometryValidator.validate_shape(plate)
        self.assertFalse(report.is_valid)
        self.assertTrue(any(issue.code == "FILLET_EXCEEDS_GEOMETRY" for issue in report.issues))


if __name__ == "__main__":
    unittest.main()
