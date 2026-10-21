"""These tests assert how a solve of either algorithm of `TOMS748` ends in these special cases:

- at an x-value where the function is exactly 0;
- on an initial interval at most ``2*xtol`` wide;
- when its evaluation budget is exhausted;
- when ``xtol`` lies below the float spacing near the root.
"""

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic


@pytest.mark.parametrize("k", [1, 2])
def test_an_exact_zero_ends_the_solve_at_that_point(k: int):
    """On a line, the secant step of step 4.1.1 lands on the root, where the function is exactly 0, and the solve
    returns the root after 3 evaluations."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize("k", [1, 2])
def test_an_initial_interval_at_most_2_xtol_wide_ends_the_solve_after_bracket_takes_the_midpoint(k: int):
    """On an initial interval at most ``2*xtol`` wide, the first call of ``bracket`` replaces the secant step by the
    midpoint, because the interval is at most ``4*delta`` wide; the solve then ends after 3 evaluations, and returns the
    midpoint of the half of the interval that holds the root.

    No stopping criterion is checked before the first call of ``bracket``, because the paper checks its termination
    test only in ``bracket``.
    """
    # --- arrange ----------------------
    a, b = 1.32471795, 1.32471796
    midpoint = 0.5 * (a + b)

    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, a, b, xtol=1e-8, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, 3)
    assert result.evaluated_x_values[2] == midpoint
    assert result.x == 0.5 * (midpoint + b)
    assert abs(result.x - CUBIC_ROOT) <= 1e-8


@pytest.mark.parametrize("k", [1, 2])
def test_an_exhausted_budget_reports_the_last_evaluated_x_value(k: int):
    """A solve whose evaluation budget runs out reports ``MAX_FEVALS``, with the last x-value that it evaluated."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-12, max_fevals=4, history_enabled=True)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.MAX_FEVALS, 4)
    assert result.x == result.evaluated_x_values[-1]


@pytest.mark.parametrize("k", [1, 2])
def test_an_xtol_below_the_float_spacing_near_the_root_ends_in_a_division_by_0(k: int):
    """An ``xtol`` of 1e-17 on ``[1, 2]`` ends the solve of `cubic` as ``SOLVER_ERROR``, with its last 3 evaluated
    x-values equal.

    That ``xtol`` lies below half the float spacing near the root of `cubic`, which is about 2.2e-16, so the interval
    never gets as narrow as ``2*xtol``.

    Once the interval is 1 float spacing wide, the midpoint that ``bracket`` takes rounds onto the lower bound, which
    ``bracket`` evaluates again, and returns both as the lower bound and as ``d``. ``Newton-Quadratic`` then divides by
    ``d - a = 0``, and `Solver.solve` records the ``ZeroDivisionError`` as ``SOLVER_ERROR``.
    """
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.SOLVER_ERROR
    assert len(set(result.evaluated_x_values[-3:])) == 1
