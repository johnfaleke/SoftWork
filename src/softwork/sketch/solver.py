"""
2D Geometric Constraint Solver for SoftWork CAD.
Implements Gauss-Newton / Levenberg-Marquardt least-squares optimization to solve 2D geometric constraints with quadratic convergence.
Calculates Degrees of Freedom (DOF) and provides convergence diagnostics.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional

from softwork.sketch.elements import Point2D, SketchElement, Line2D, Circle2D, Rectangle2D
from softwork.sketch.constraints import Constraint, ConstraintType


@dataclass
class SolverReport:
    is_converged: bool
    iterations: int
    residual_error: float
    degrees_of_freedom: int
    unresolved_constraints: List[str] = field(default_factory=list)


def _solve_linear_system(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
    """Solves A * x = b using Gaussian elimination with partial pivoting."""
    n = len(A)
    if n == 0 or len(b) != n:
        return None

    # Augment matrix
    M = [A[i][:] + [b[i]] for i in range(n)]

    for i in range(n):
        # Pivot
        max_row = i
        max_val = abs(M[i][i])
        for k in range(i + 1, n):
            if abs(M[k][i]) > max_val:
                max_val = abs(M[k][i])
                max_row = k
        if max_val < 1e-12:
            return None  # Singular or rank-deficient
        M[i], M[max_row] = M[max_row], M[i]

        pivot = M[i][i]
        for j in range(i, n + 1):
            M[i][j] /= pivot

        for k in range(n):
            if k != i:
                factor = M[k][i]
                for j in range(i, n + 1):
                    M[k][j] -= factor * M[i][j]

    return [M[i][n] for i in range(n)]


class ConstraintSolver:
    """
    Solves 2D geometric constraints for parametric sketches.
    """

    def __init__(self, max_iterations: int = 50, tolerance: float = 1e-3) -> None:
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def solve(self, elements: List[SketchElement], constraints: List[Constraint]) -> SolverReport:
        if not constraints:
            dof = self._calculate_dof(elements, constraints)
            return SolverReport(is_converged=True, iterations=0, residual_error=0.0, degrees_of_freedom=dof)

        # 1. Collect point variables: name -> [u, v]
        point_vars: Dict[str, List[float]] = {}
        elements_map: Dict[str, SketchElement] = {}

        for el in elements:
            elements_map[el.id] = el
            if isinstance(el, Line2D):
                point_vars[f"{el.id}_start"] = [el.start.u, el.start.v]
                point_vars[f"{el.id}_end"] = [el.end.u, el.end.v]
            elif isinstance(el, Circle2D):
                point_vars[f"{el.id}_center"] = [el.center.u, el.center.v]
            elif isinstance(el, Rectangle2D):
                point_vars[f"{el.id}_c"] = [el.center_u, el.center_v]

        var_keys = sorted(point_vars.keys())
        if not var_keys:
            dof = self._calculate_dof(elements, constraints)
            return SolverReport(is_converged=True, iterations=0, residual_error=0.0, degrees_of_freedom=dof)

        # Map each variable to 2 parameters (u index = 2*i, v index = 2*i + 1)
        num_vars = len(var_keys) * 2
        var_index_map: Dict[str, Tuple[int, int]] = {}
        x = [0.0] * num_vars
        for i, vk in enumerate(var_keys):
            var_index_map[vk] = (2 * i, 2 * i + 1)
            x[2 * i] = point_vars[vk][0]
            x[2 * i + 1] = point_vars[vk][1]

        def get_points(vec: List[float]) -> Dict[str, Point2D]:
            pts: Dict[str, Point2D] = {}
            for k, (iu, iv) in var_index_map.items():
                pts[k] = Point2D(vec[iu], vec[iv])
            return pts

        iter_count = 0
        final_err = 0.0
        damping = 1e-3

        for iteration in range(self.max_iterations):
            iter_count = iteration + 1
            cur_points = get_points(x)

            # Compute residuals vector r
            residuals: List[float] = []
            for c in constraints:
                res = c.residual(cur_points, elements_map)
                residuals.append(res)

            final_err = max(abs(r) for r in residuals) if residuals else 0.0
            if final_err < self.tolerance:
                break

            # Compute Jacobian J (m constraints x n variables) via finite difference
            m = len(constraints)
            n = num_vars
            J: List[List[float]] = [[0.0] * n for _ in range(m)]
            delta = 1e-5

            for j in range(n):
                x[j] += delta
                pts_delta = get_points(x)
                for i, c in enumerate(constraints):
                    res_delta = c.residual(pts_delta, elements_map)
                    J[i][j] = (res_delta - residuals[i]) / delta
                x[j] -= delta

            # Form normal equations: (J^T * J + lambda * I) * dx = -J^T * r
            JTJ = [[0.0] * n for _ in range(n)]
            JTr = [0.0] * n

            for i in range(n):
                for j in range(n):
                    sum_val = sum(J[k][i] * J[k][j] for k in range(m))
                    JTJ[i][j] = sum_val
                JTJ[i][i] += damping
                JTr[i] = -sum(J[k][i] * residuals[k] for k in range(m))

            # Solve linear system
            dx = _solve_linear_system(JTJ, JTr)
            if dx is None:
                # Fallback to damped gradient step
                for i in range(n):
                    x[i] += 0.1 * JTr[i]
            else:
                for i in range(n):
                    x[i] += dx[i]

        # 3. Apply solved values back
        solved_points = get_points(x)
        for el in elements:
            if isinstance(el, Line2D):
                if f"{el.id}_start" in solved_points:
                    el.start.u = solved_points[f"{el.id}_start"].u
                    el.start.v = solved_points[f"{el.id}_start"].v
                if f"{el.id}_end" in solved_points:
                    el.end.u = solved_points[f"{el.id}_end"].u
                    el.end.v = solved_points[f"{el.id}_end"].v
            elif isinstance(el, Circle2D):
                if f"{el.id}_center" in solved_points:
                    el.center.u = solved_points[f"{el.id}_center"].u
                    el.center.v = solved_points[f"{el.id}_center"].v
            elif isinstance(el, Rectangle2D):
                if f"{el.id}_c" in solved_points:
                    el.center_u = solved_points[f"{el.id}_c"].u
                    el.center_v = solved_points[f"{el.id}_c"].v

        # 4. Check satisfaction
        unresolved = []
        for c in constraints:
            r = c.residual(solved_points, elements_map)
            c.is_satisfied = (abs(r) < self.tolerance * 5.0)
            if not c.is_satisfied:
                unresolved.append(c.name)

        dof = self._calculate_dof(elements, constraints)
        is_converged = (len(unresolved) == 0)

        return SolverReport(
            is_converged=is_converged,
            iterations=iter_count,
            residual_error=final_err,
            degrees_of_freedom=dof,
            unresolved_constraints=unresolved,
        )

    def _calculate_dof(self, elements: List[SketchElement], constraints: List[Constraint]) -> int:
        num_vars = 0
        for el in elements:
            if isinstance(el, Line2D):
                num_vars += 4
            elif isinstance(el, Circle2D):
                num_vars += 3
            elif isinstance(el, Rectangle2D):
                num_vars += 4
            else:
                num_vars += 2
        return max(0, num_vars - len(constraints))
