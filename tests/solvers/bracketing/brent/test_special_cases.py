"""These tests assert that an exact zero ends a `Brent` solve at that x-value, and that `Brent` never meets its
stopping rule when ``xtol`` is so small that Brent's internal tolerance ``tol`` becomes negative."""

from sunnbear.solvers import Brent, SolveStatus
from tests.solvers.example_functions import cubic


def test_an_exact_zero_ends_the_solve_at_that_point():
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = Brent().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


def test_an_xtol_that_makes_tol_negative_is_never_met():
    """An ``xtol`` of 1e-17 on ``[1, 2]`` makes Brent's tolerance ``tol`` negative, so the solve exhausts its
    budget."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
