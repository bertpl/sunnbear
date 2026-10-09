"""These tests assert that the individual steps of `TOMS748` follow the authors' code."""

import pytest

from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize("k", [1, 2])
def test_the_first_step_is_a_secant_step(k):
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step to 1 + 1/6."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize("k", [1, 2])
def test_a_point_close_to_a_bound_moves_to_the_margin_and_the_lower_bound_is_returned(k):
    """On ``x - 1e-9`` over ``[0, 1]`` with ``xtol = 1e-4``, the secant point 1e-9 lies within ``0.7 * stop_width``
    of the lower bound, so the secant point moves to ``0.7 * stop_width``. The interval ``[0, 0.7 * stop_width]``
    that remains meets the stopping criterion, and the solve returns its lower bound 0."""
    # --- arrange ----------------------
    xtol = 1e-4
    # The lower bound has the smaller |f|, and lies at 0, so stop_width is 2 * tol.
    stop_width = 2.0 * (0.5 * xtol - 2.0 * FLOAT64_EPS * 1.0)

    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 1e-9, 0.0, 1.0, xtol=xtol, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 0.7 * stop_width
    assert (result.x, result.status, result.n_fevals) == (0.0, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize(
    "fa, fb, fd, expected",
    [
        # The points (0, -1), (1, 1) and (2, 3) lie on the line 2x - 1, so f[a, b, d] = 0.
        (-1.0, 1.0, 3.0, 0.5),
        # The quadratic through a = 0, b = 1 and d = 2 is p(x) = -1 - x - x(x - 1); the steps start at a, where
        # p'(0) = -1 + 1 = 0.
        (-1.0, -2.0, -5.0, -1.0),
    ],
    ids=["points_on_a_line", "zero_derivative"],
)
def test_newton_quadratic_zero_returns_the_zero_of_the_line_through_a_and_b_when_newton_steps_cannot_be_taken(
    fa, fb, fd, expected
):
    """When ``f[a, b, d] = 0``, or when a Newton step meets a zero derivative of the quadratic, Newton-Quadratic
    returns the zero of the line through ``a`` and ``b``."""
    # --- act / assert -----------------
    assert TOMS748._newton_quadratic_zero(0.0, 1.0, 2.0, fa, fb, fd, 2) == expected
