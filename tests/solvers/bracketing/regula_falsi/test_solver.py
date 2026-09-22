"""These tests assert `RegulaFalsi` in both cases of its known weakness: it converges on a chord, stalls on a curve."""

import pytest

from sunnbear.solvers import RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic


# ==================================================================================================
#  Convergence and the stall
# ==================================================================================================
@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The parametrization exercises both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    # --- act --------------------------
    result = RegulaFalsi().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    # The chord is the function, so the first iterate is the exact root and the stopping criterion holds immediately.
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_a_convex_function_stalls_on_the_retained_bound_and_exhausts_the_budget():
    # --- act --------------------------
    result = RegulaFalsi().solve(cubic, 1.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    # The iterates converge to the root, but the upper bound never moves, so the stopping criterion never holds.
    x_last, _ = result.history[-1]
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 60
    assert abs(x_last - CUBIC_ROOT) <= 1e-9
    assert result.x == x_last  # The reported estimate is the last evaluated point, not the retained bound.


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    # --- act --------------------------
    result = RegulaFalsi().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (RegulaFalsi.name, RegulaFalsi.version) == ("regula_falsi", 1)
    assert result.flop_counts.total_count() > 0
