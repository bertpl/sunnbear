"""These tests assert how `TOMS748` handles 4 special cases:

- an exact zero;
- an initial interval at most ``2*xtol`` wide;
- a solve that exhausts its evaluation budget;
- an ``xtol`` below the float spacing near the root.
"""

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic


@pytest.mark.parametrize("k", [1, 2])
def test_an_exact_zero_ends_the_solve_at_that_point(k):
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


def test_an_initial_interval_at_most_2_xtol_wide_returns_its_midpoint_without_an_interior_evaluation():
    """An initial interval of width 1e-12, below ``2*xtol = 2e-10``, already meets the stopping criterion, so the solve
    returns its midpoint after the 2 evaluations at its bounds."""
    # --- arrange ----------------------
    a, b = CUBIC_ROOT - 5e-13, CUBIC_ROOT + 5e-13

    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, a, b, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5 * (a + b), SolveStatus.CONVERGED, 2)


@pytest.mark.parametrize("k", [1, 2])
def test_a_solve_that_exhausts_its_budget_reports_the_latest_evaluated_x_value(k):
    """A budget of 4 evaluations ends the solve on `cubic` over ``[1, 2]`` before it converges, and the solve reports
    the x-value of its 4th evaluation."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=4, history_enabled=True)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.MAX_FEVALS, 4)
    assert result.x == result.history[-1][0]


@pytest.mark.parametrize("k", [1, 2])
def test_an_xtol_below_the_float_spacing_near_the_root_ends_the_solve_as_a_solver_error(k):
    """An ``xtol`` of 1e-17 on ``[1, 2]`` lies below the float spacing near the root, so the interval never shrinks to
    ``2*xtol``.

    Once the interval is 1 float spacing wide, its midpoint rounds onto a bound, which then also becomes ``d``, the
    bound that `TOMS748` most recently discarded, and the next call of Newton-Quadratic divides by ``d - a = 0``.
    """
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.SOLVER_ERROR
