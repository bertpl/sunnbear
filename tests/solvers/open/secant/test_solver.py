"""These tests assert how `Secant` starts, steps and stops, and the ways in which its solve can fail."""

import pytest

from sunnbear.solvers import Secant, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, STEEP_EXPONENTIAL_ROOT, cubic, steep_exponential


def _unit_jump_at_half(x: float) -> float:
    """Return -1 left of 0.5 and 1 from 0.5 on."""
    if x < 0.5:
        return -1.0
    else:
        return 1.0


# ==================================================================================================
#  Steps and stopping
# ==================================================================================================
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


def test_the_returned_point_is_the_next_point_without_its_evaluation():
    """`Secant` stops once the step from the newest point is at most ``xtol``, and returns the next point without
    evaluating it."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    evaluated_x_values = result.evaluated_x_values
    assert result.status is SolveStatus.CONVERGED
    assert result.x not in evaluated_x_values
    assert abs(result.x - evaluated_x_values[-1]) <= 1e-10
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


def test_a_smooth_function_converges_in_few_evaluations():
    """On the cubic, near which the secant method converges faster than linearly, `Secant` reaches ``xtol = 1e-10``
    within 10 evaluations."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals <= 10


# ==================================================================================================
#  Failures of an open method
# ==================================================================================================
def test_equal_function_values_at_the_2_latest_points_end_the_solve_as_diverged():
    """On `_unit_jump_at_half` over ``[0, 1]``, the first iterate, 0.5, has the same value as ``b``, so the next secant
    is horizontal and the solve ends as ``DIVERGED``."""
    # --- act --------------------------
    result = Secant().solve(_unit_jump_at_half, 0.0, 1.0, xtol=1e-9, max_fevals=60)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.DIVERGED, 3)


def test_a_step_from_a_flat_region_leaves_the_interval():
    """On `steep_exponential` over ``[0, 1]``, which is nearly flat left of its root, the third secant runs through 2
    points near 0 with nearly equal values and lands near 500, where the function overflows, so the solve ends as
    ``DIVERGED``."""
    # --- act --------------------------
    result = Secant().solve(steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.DIVERGED


def test_a_small_step_in_a_flat_region_stops_far_from_the_root():
    """On `steep_exponential` over ``[0, 1]`` with ``xtol = 1e-4``, the second step, near 0, is shorter than ``xtol``,
    so `Secant` stops near 4e-5, far from the root near 0.46."""
    # --- act --------------------------
    result = Secant().solve(steep_exponential, 0.0, 1.0, xtol=1e-4, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - STEEP_EXPONENTIAL_ROOT) > 0.4


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Secant` is named ``secant``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Secant.name, Secant.version) == ("secant", 1)
    assert result.flop_counts.total_count() > 0
