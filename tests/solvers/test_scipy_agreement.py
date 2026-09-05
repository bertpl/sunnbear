"""`Bisection` agrees with `scipy.optimize.bisect` when both run under the `Solver` template method."""

import pytest
from scipy import optimize

from sunnbear.functions import FormulaRegistry
from sunnbear.solvers import Bisection, SolveStatus

from .scipy_solver import ScipySolver


def _cube_minus_two(x: float) -> float:
    return x**3 - 2.0


def _catalog_cubic(x: float) -> float:
    return FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0).build_x_fun(1.0)(x)


@pytest.mark.parametrize(
    "f, a, b", [(_cube_minus_two, 0.0, 2.0), (lambda x: 0.3 - x, 0.0, 1.0), (_catalog_cubic, -2.0, 2.0)]
)
@pytest.mark.parametrize("xtol", [1e-4, 1e-9])
def test_bisection_agrees_with_scipy_bisect(f, a, b, xtol):
    # --- act --------------------------
    ours = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)
    scipy_result = ScipySolver(optimize.bisect).solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert ours.status is scipy_result.status is SolveStatus.CONVERGED
    assert ours.x == scipy_result.x  # SciPy's last midpoint is the midpoint of our final bracket.
    # Two of the three are the endpoint re-evaluations (see ScipySolver); the third is SciPy halving once
    # more, since it stops below xtol where Interval.is_converged stops at 2 * xtol.
    assert scipy_result.n_fevals == ours.n_fevals + 3


def test_scipy_solver_reports_no_iterations_and_no_flops():
    """SciPy's loop runs on plain floats outside our arithmetic, so only evaluations are measured."""
    # --- act --------------------------
    scipy_result = ScipySolver(optimize.bisect).solve(_cube_minus_two, 0.0, 2.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert scipy_result.n_iters is None
    assert scipy_result.flop_counts.total_count() == 0
    assert scipy_result.n_fevals > 2


def test_scipy_solver_is_subject_to_the_budget():
    """The wrapper's budget ends a SciPy solve the same way it ends ours."""
    # --- act --------------------------
    scipy_result = ScipySolver(optimize.bisect).solve(_cube_minus_two, 0.0, 2.0, xtol=1e-12, max_fevals=5)

    # --- assert -----------------------
    assert (scipy_result.status, scipy_result.n_fevals) == (SolveStatus.MAX_FEVALS, 5)
