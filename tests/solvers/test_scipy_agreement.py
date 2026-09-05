"""Agreement of the reference solvers with their `scipy.optimize` counterparts, run under the same template method."""

import pytest
from scipy import optimize

from sunnbear.functions import FormulaRegistry
from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.scipy_twin import ScipySolver


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
    twin = ScipySolver(optimize.bisect).solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert ours.status is twin.status is SolveStatus.CONVERGED
    assert ours.x == twin.x  # SciPy's last midpoint is the midpoint of our final bracket.
    # SciPy re-evaluates the two endpoints the template method already evaluated, and it halves once more
    # than we do: it stops at a bracket width below xtol, where our criterion stops at 2 * xtol.
    assert twin.n_fevals == ours.n_fevals + 3


def test_twin_reports_no_iterations_and_no_flops():
    """SciPy's loop runs on plain floats outside our arithmetic, so the twin measures evaluations only."""
    # --- act --------------------------
    twin = ScipySolver(optimize.bisect).solve(_cube_minus_two, 0.0, 2.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert twin.n_iters is None
    assert twin.flop_counts.total_count() == 0
    assert twin.n_fevals > 2


def test_twin_is_subject_to_the_budget():
    """The wrapper's budget ends a SciPy solve the same way it ends ours."""
    # --- act --------------------------
    twin = ScipySolver(optimize.bisect).solve(_cube_minus_two, 0.0, 2.0, xtol=1e-12, max_fevals=5)

    # --- assert -----------------------
    assert (twin.status, twin.n_fevals) == (SolveStatus.MAX_FEVALS, 5)
