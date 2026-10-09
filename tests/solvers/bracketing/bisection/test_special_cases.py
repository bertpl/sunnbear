"""These tests assert that `Bisection` stops early on an exact root at a midpoint, and that it reports the last
evaluated x-value when its budget runs out."""

from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.example_functions import cubic


def test_an_exact_midpoint_root_stops_early():
    """`Bisection` stops after 3 evaluations when the first midpoint, 0.5, is an exact root."""
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


def test_running_out_of_budget_reports_the_last_evaluated_point():
    """When its budget runs out, `Bisection` reports ``MAX_FEVALS`` with the last evaluated midpoint as
    ``result.x``."""
    # --- act --------------------------
    result = Bisection().solve(cubic, 1.0, 2.0, xtol=1e-12, max_fevals=6)

    # --- assert -----------------------
    # After the 2 bound evaluations, 4 steps evaluated the midpoints 1.5, 1.25, 1.375, and 1.3125.
    assert (result.status, result.n_fevals, result.x) == (SolveStatus.MAX_FEVALS, 6, 1.3125)
