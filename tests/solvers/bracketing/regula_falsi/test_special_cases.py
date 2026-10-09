"""These tests assert that `RegulaFalsi` stalls on a convex function and runs out of its budget."""

from sunnbear.solvers import RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic


def test_a_convex_function_stalls_on_the_retained_bound_and_exhausts_the_budget():
    """On `cubic`, the iterates of `RegulaFalsi` reach the root while the upper interval bound never moves, so the solve
    uses up its budget and reports the last evaluated x-value."""
    # --- act --------------------------
    result = RegulaFalsi().solve(cubic, 1.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    # The iterates converge to the root, but the upper bound never moves, so the stopping criterion never holds.
    x_last, _ = result.history[-1]
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 60
    assert abs(x_last - CUBIC_ROOT) <= 1e-9
    assert result.x == x_last  # The reported estimate is the last evaluated point, not the retained bound.
