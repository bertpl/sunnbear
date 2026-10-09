"""These tests assert that an exact zero ends a `SteffenBrent` solve without evaluating the midpoint."""

from sunnbear.solvers import SolveStatus, SteffenBrent


def test_an_exact_zero_ends_the_solve_without_evaluating_the_midpoint():
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = SteffenBrent().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)
