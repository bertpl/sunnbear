"""These tests assert that the individual steps of `ModAB` follow its algorithm, and that it stops by the shared
stopping criterion."""

from sunnbear.solvers import ModAB, SolveStatus
from tests.solvers.example_functions import cubic


def test_the_first_step_is_a_bisection():
    """`ModAB` starts in bisection mode, so its first x-value is the midpoint of the interval."""
    # --- act --------------------------
    result = ModAB().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 1.5


def test_a_straight_line_switches_to_anderson_bjorck_whose_first_step_lands_on_the_root():
    """On a line, the midpoint lies exactly on the secant, so the method switches to Anderson-Björck mode, and the
    secant's zero is the root, where the function is exactly 0: 4 evaluations in total."""
    # --- act --------------------------
    result = ModAB().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values == (0.0, 1.0, 0.5, 0.25)
    assert (result.x, result.status) == (0.25, SolveStatus.CONVERGED)


def test_the_solve_returns_the_midpoint_of_an_interval_at_most_2_xtol_wide():
    """`ModAB` stops once the interval is at most ``2*xtol`` wide, and returns its midpoint; on the increasing
    `cubic`, the final interval's bounds are the evaluated x-values closest to the root on either side."""
    # --- act --------------------------
    result = ModAB().solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    x1 = max(x for x, fx in result.history if fx < 0.0)
    x2 = min(x for x, fx in result.history if fx > 0.0)
    assert x2 - x1 <= 2e-6
    assert result.x == 0.5 * (x1 + x2)
