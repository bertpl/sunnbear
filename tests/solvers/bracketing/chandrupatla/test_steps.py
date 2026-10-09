"""These tests assert that the individual steps of `Chandrupatla` follow its algorithm."""

from sunnbear.solvers import Chandrupatla
from tests.solvers.example_functions import cubic


def test_the_first_step_is_a_bisection():
    """`Chandrupatla` starts with ``t = 0.5``, so its first point is the midpoint of the interval."""
    # --- act --------------------------
    result = Chandrupatla().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 1.5
