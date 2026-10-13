"""These tests assert that the individual steps of `SteffenBrent` follow its algorithm."""

import math

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent
from tests.solvers.example_functions import cubic


def _saturating_exponential(x: float) -> float:
    """Return ``1 - 11 * exp(-24 * x)``; its value stays close to 1 on most of ``[0, 1]``, and its root is
    ``ln(11) / 24``."""
    return 1.0 - 11.0 * math.exp(-24.0 * x)


def test_the_first_step_is_a_secant_step_from_the_bound_with_the_smaller_abs_f():
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step from 1 to
    1 + 1/6."""
    # --- act --------------------------
    result = SteffenBrent().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


def test_the_modification_evaluates_the_midpoint_of_a_and_s_and_interpolation_is_exact_for_a_quadratic_inverse():
    """On ``sqrt(x) - 1/2`` over ``[0, 1]``, the first step lands on 0.5, and the modification evaluates 0.25, the
    midpoint of ``a = 0`` and ``s = 0.5``. 0.25 is the root, but its value 0 does not differ in sign from ``f(s)``, so
    the solve goes on, and the second step, an inverse quadratic interpolation, lands on the root up to rounding,
    because the inverse function ``(y + 1/2)^2`` is quadratic."""
    # --- act --------------------------
    result = SteffenBrent().solve(
        lambda x: math.sqrt(x) - 0.5, 0.0, 1.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values[:4] == (0.0, 1.0, 0.5, 0.25)
    assert result.evaluated_x_values[4] == pytest.approx(0.25, abs=1e-16)


def test_the_interval_does_not_always_halve():
    """On ``1 - 11 * exp(-24 * x)`` over ``[0, 1]``, the first step evaluates ``s`` near 0.91 and the midpoint
    ``m = s / 2`` of 0 and ``s``; ``f(m)`` has the sign of ``f(s)``, so the interval keeps ``[0, s]``, 91 % of its
    width, and the next x-value, the bisection of ``[0, s]``, is ``m`` again."""
    # --- act --------------------------
    result = SteffenBrent().solve(_saturating_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    s, m, next_x = result.evaluated_x_values[2:5]
    assert s == pytest.approx(0.91, abs=0.01)
    assert m == s / 2.0
    assert next_x == m


def test_equal_function_values_at_b_and_b_previous_force_a_bisection():
    """On ``1 - 11 * exp(-24 * x)`` over ``[0, 1]``, the swap at the end of an iteration, which keeps the smaller
    ``|f|`` in ``b``, makes ``b`` equal ``b_previous`` in several iterations, where the secant of the paper's
    Algorithm 2 divides 0 by 0; `SteffenBrent` bisects there, and returns a root within ``xtol``."""
    # --- act --------------------------
    result = SteffenBrent().solve(_saturating_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - math.log(11.0) / 24.0) <= 1e-10
