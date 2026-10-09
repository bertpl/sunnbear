"""These tests assert how `Secant` fails as an open method: on equal function values, and in flat regions."""

from sunnbear.solvers import Secant, SolveStatus
from tests.solvers.example_functions import STEEP_EXPONENTIAL_ROOT, steep_exponential


def _unit_jump_at_half(x: float) -> float:
    """Return -1 left of 0.5 and 1 from 0.5 on."""
    if x < 0.5:
        return -1.0
    else:
        return 1.0


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
