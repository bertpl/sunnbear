"""These tests assert how `TOMS748` handles 3 special cases:

- an exact zero;
- an initial interval narrower than ``xtol``;
- an ``xtol`` below the machine precision.
"""

import sys

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic

_MACHEPS = sys.float_info.epsilon


@pytest.mark.parametrize("k", [1, 2])
def test_an_exact_zero_ends_the_solve_at_that_point(k):
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


def test_an_initial_interval_narrower_than_stop_width_returns_its_lower_bound_without_an_interior_evaluation():
    """An initial interval of width 1e-12, below ``xtol = 1e-10``, already meets the stopping criterion, so the solve
    returns its lower bound after the 2 evaluations at its bounds."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, CUBIC_ROOT - 5e-13, CUBIC_ROOT + 5e-13, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (CUBIC_ROOT - 5e-13, SolveStatus.CONVERGED, 2)


def test_an_xtol_below_the_machine_precision_sets_tol_to_0():
    """An ``xtol`` of 1e-17 on ``[1, 2]`` would make ``tol`` negative; with ``tol = 0``, the solve still converges,
    within ``stop_width = 4 * macheps * |u|`` of the root."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 4.0 * _MACHEPS * 2.0
