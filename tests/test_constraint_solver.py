"""
Tests for 2D Geometric Constraint Solver (SolveSpace-style numerical relaxation).
"""
import unittest
from softwork.sketch.elements import Point2D, Line2D, Circle2D, Rectangle2D
from softwork.sketch.constraints import (
    CoincidentConstraint,
    HorizontalConstraint,
    VerticalConstraint,
    DistanceConstraint,
    LengthConstraint,
    RadiusConstraint,
    FixedConstraint,
)
from softwork.sketch.sketch import Sketch
from softwork.sketch.solver import ConstraintSolver


class TestConstraintSolver(unittest.TestCase):
    def test_horizontal_and_vertical_constraints(self):
        sketch = Sketch(name="HVTest")
        # Line from (0, 5) to (50, 12)
        l1 = sketch.add_line(0.0, 5.0, 50.0, 12.0)
        
        # Add Horizontal Constraint
        c_h = HorizontalConstraint(point_a_id=f"{l1.id}_start", point_b_id=f"{l1.id}_end")
        sketch.add_constraint(c_h)

        report = sketch.solve()
        self.assertTrue(report.is_converged)
        self.assertAlmostEqual(l1.start.v, l1.end.v, delta=1e-2)

    def test_coincident_and_fixed_constraints(self):
        sketch = Sketch(name="CoincidentTest")
        l1 = sketch.add_line(10.0, 10.0, 40.0, 10.0)
        l2 = sketch.add_line(45.0, 15.0, 45.0, 40.0)

        # Fix start of l1 at (0, 0)
        c_fix = FixedConstraint(point_id=f"{l1.id}_start", fixed_u=0.0, fixed_v=0.0)
        # Make end of l1 coincident with start of l2
        c_coin = CoincidentConstraint(point_a_id=f"{l1.id}_end", point_b_id=f"{l2.id}_start")
        
        sketch.add_constraint(c_fix)
        sketch.add_constraint(c_coin)

        report = sketch.solve()
        self.assertTrue(report.is_converged)
        self.assertAlmostEqual(l1.start.u, 0.0, delta=1e-2)
        self.assertAlmostEqual(l1.start.v, 0.0, delta=1e-2)
        self.assertAlmostEqual(l1.end.u, l2.start.u, delta=1e-2)
        self.assertAlmostEqual(l1.end.v, l2.start.v, delta=1e-2)

    def test_dof_calculation(self):
        sketch = Sketch(name="DOFTest")
        l1 = sketch.add_line(0.0, 0.0, 20.0, 0.0)
        c1 = sketch.add_circle(10.0)
        # Elements: 1 line (4 vars) + 1 circle (3 vars) = 7 vars
        # 1 constraint
        sketch.add_constraint(RadiusConstraint(circle_id=c1.id, radius=15.0))
        report = sketch.solve()
        self.assertEqual(report.degrees_of_freedom, 6)


if __name__ == "__main__":
    unittest.main()
