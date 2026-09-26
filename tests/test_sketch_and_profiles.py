"""
Tests for 2D sketch plane, elements, closed profiles, and loop detection.
"""
import unittest
from softwork.sketch.plane import SketchPlane, StandardPlane
from softwork.sketch.elements import Point2D, Line2D, Circle2D, Rectangle2D, Polygon2D
from softwork.sketch.profile import SketchProfile
from softwork.sketch.sketch import Sketch


class TestSketchAndProfiles(unittest.TestCase):
    def test_sketch_plane_transformation(self):
        plane_xy = SketchPlane.from_standard(StandardPlane.XY, offset=10.0)
        p3_xy = plane_xy.to_3d(5.0, 15.0, 0.0)
        self.assertEqual(p3_xy.x, 5.0)
        self.assertEqual(p3_xy.y, 15.0)
        self.assertEqual(p3_xy.z, 10.0)

        plane_xz = SketchPlane.from_standard(StandardPlane.XZ)
        p3_xz = plane_xz.to_3d(10.0, 20.0, 0.0)
        self.assertEqual(p3_xz.x, 10.0)
        self.assertEqual(p3_xz.y, 0.0)
        self.assertEqual(p3_xz.z, 20.0)

    def test_rectangle_profile_and_area(self):
        rect = Rectangle2D(width=100.0, height=50.0, centered=True)
        pts = rect.sample_points()
        self.assertEqual(len(pts), 4)

        prof = SketchProfile.from_element(rect)
        self.assertIsNotNone(prof)
        self.assertTrue(prof.is_closed)
        self.assertEqual(prof.area(), 5000.0)

    def test_circle_profile_and_area(self):
        circ = Circle2D(center=Point2D(0.0, 0.0), radius=10.0)
        prof = SketchProfile.from_element(circ)
        self.assertIsNotNone(prof)
        self.assertTrue(prof.is_closed)
        # 32-segment polygon area approximation of circle
        self.assertAlmostEqual(prof.area(), 314.159, delta=10.0)

    def test_sketch_container_profile_detection(self):
        sk = Sketch(name="TestSketch")
        self.assertIsNone(sk.primary_profile)

        sk.add_rectangle(width=80.0, height=40.0)
        self.assertIsNotNone(sk.primary_profile)
        self.assertEqual(len(sk.profiles), 1)
        self.assertEqual(sk.primary_profile.area(), 3200.0)


if __name__ == "__main__":
    unittest.main()
