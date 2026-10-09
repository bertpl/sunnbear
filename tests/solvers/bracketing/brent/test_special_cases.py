"""These tests assert that `Brent` never meets its stopping rule when ``xtol`` makes its tolerance negative."""

from sunnbear.solvers import Brent, SolveStatus
from tests.solvers.example_functions import cubic


def test_an_xtol_that_makes_tol_negative_is_never_met():
    """An ``xtol`` of 1e-17 on ``[1, 2]`` makes Brent's tolerance ``tol`` negative, so the solve exhausts its
    budget."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
