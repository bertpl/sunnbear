"""These tests assert that an exact zero ends a `CARF` solve at that x-value."""

from sunnbear.solvers import CARF, SolveStatus


def test_an_exact_zero_ends_the_solve_at_that_point():
    """On a straight line, the chord's zero is the root, so the first x-value has a function value of exactly 0, and
    the solve returns it after 3 evaluations."""
    # --- act --------------------------
    result = CARF().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)
