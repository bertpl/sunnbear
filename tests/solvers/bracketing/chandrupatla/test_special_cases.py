"""These tests assert that an exact zero ends a `Chandrupatla` solve at that x-value."""

from sunnbear.solvers import Chandrupatla, SolveStatus


def test_an_exact_zero_ends_the_solve_at_that_point():
    """A midpoint that is exactly the root ends the solve after 3 evaluations, the 2 bounds and that midpoint."""
    # --- act --------------------------
    result = Chandrupatla().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)
