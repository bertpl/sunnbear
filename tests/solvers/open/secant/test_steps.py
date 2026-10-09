"""These tests assert that the individual steps of `Secant` follow SciPy's secant method."""

import pytest

from sunnbear.solvers import Secant, SolveStatus
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first secant lands on the root, so `Secant` stops after the 2 bound evaluations and 1
    iterate."""
    # --- act --------------------------
    result = Secant().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, 3)
    assert abs(result.x - 0.3) <= 1e-12


@pytest.mark.parametrize(
    "b, is_bound_a_kept", [(1.5, True), (2.0, False)]
)  # |f(1.5)| < |f(1)| < |f(2)|, so the 2 cases cover both orders of |f| at the starting points.
def test_the_second_step_keeps_the_starting_point_with_the_larger_abs_f(b, is_bound_a_kept):
    """On the cubic over ``[1, b]``, the second secant runs through the first iterate and the starting point with the
    larger ``|f|``, as in SciPy."""
    # --- arrange ----------------------
    a = 1.0

    # --- act --------------------------
    history = Secant().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (_, fa), (_, fb), (x2, f2), (x3, _) = history[:4]
    x_kept, f_kept = (a, fa) if is_bound_a_kept else (b, fb)
    assert x3 == pytest.approx((x_kept * f2 - x2 * f_kept) / (f2 - f_kept), rel=1e-12, abs=0.0)
