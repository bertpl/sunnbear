"""These tests assert that `SteffenBrent` reproduces the case studies of its paper, takes the steps of the paper's
Algorithm 2, and stops within ``xtol`` of a root."""

import math

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


def _case_study_1(x: float) -> float:
    """Return the function of the paper's first case study, its equation 6."""
    return math.exp(-(x**2) / 4.0) - 2.0 * math.cos(x) + x / 2.0 - 2.5


# The Peng-Robinson constants, at full precision (Peng and Robinson, 1976): the paper prints them rounded to
# Λ = 0.45724 and Γ = 0.07780, but its root fits the full-precision constants to within 6.5e-9; the rounded ones move
# the root by 6.6e-4.
_PENG_ROBINSON_ETA = 1.0 / (1.0 + (4.0 - math.sqrt(8.0)) ** (1.0 / 3.0) + (4.0 + math.sqrt(8.0)) ** (1.0 / 3.0))
_PENG_ROBINSON_CAPITAL_LAMBDA = (8.0 + 40.0 * _PENG_ROBINSON_ETA) / (49.0 - 37.0 * _PENG_ROBINSON_ETA)
_PENG_ROBINSON_CAPITAL_GAMMA = _PENG_ROBINSON_ETA / (3.0 + _PENG_ROBINSON_ETA)


def _case_study_2(v: float) -> float:
    """Return the function of the paper's second case study: its equation 8 with the Peng-Robinson parameters of its
    equation 9, at ``omega = 0.2``, ``Tr = 0.85`` and ``Pr = 0.45``, where ``v`` is the volume ``V`` divided by the
    co-volume parameter ``b``."""
    lam, sigma, omega, tr, pr = 2.0, -1.0, 0.2, 0.85, 0.45
    alpha = (1.0 + (0.37464 + 1.54226 * omega - 0.26992 * omega**2) * (1.0 - math.sqrt(tr))) ** 2
    t = tr / (_PENG_ROBINSON_CAPITAL_GAMMA * pr)
    u = _PENG_ROBINSON_CAPITAL_LAMBDA * alpha / (_PENG_ROBINSON_CAPITAL_GAMMA**2 * pr)
    return v**3 - (1.0 - lam + t) * v**2 + (sigma - lam - lam * t + u) * v - (sigma + sigma * t + u)


def _steep_exponential(x: float) -> float:
    """Return ``1 - 11 * exp(-24 * x)``; it is flat near 1 on most of ``[0, 1]``, with its root at ``ln(11) / 24``."""
    return 1.0 - 11.0 * math.exp(-24.0 * x)


# ==================================================================================================
#  The paper's case studies
# ==================================================================================================
def test_case_study_1_reaches_the_papers_root_in_its_6_iterations():
    """On the paper's first case study over ``[1, 3]``, `SteffenBrent` returns the paper's root 2.1584212093.

    The 11 evaluations are the 2 at the interval bounds, 1 in each of the paper's 6 iterations, and 3 more at the
    midpoint.
    """
    # --- act --------------------------
    result = SteffenBrent().solve(_case_study_1, 1.0, 3.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(2.1584212093, abs=5e-11)
    assert result.n_fevals == 11


def test_case_study_2_reaches_the_papers_root():
    """On the paper's second case study over ``[14, 17]``, at the paper's tolerance of 1e-10, `SteffenBrent` returns a
    root within 1e-8 of the paper's root 15.0676609061.

    The paper's root and the root of the cubic at the full-precision constants differ by 6.5e-9.
    """
    # --- act --------------------------
    result = SteffenBrent().solve(_case_study_2, 14.0, 17.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(15.0676609061, abs=1e-8)


# ==================================================================================================
#  The steps
# ==================================================================================================
def test_the_first_step_is_a_secant_step_from_the_bound_with_the_smaller_abs_f():
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step from 1 to
    1 + 1/6."""
    # --- act --------------------------
    result = SteffenBrent().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


def test_a_step_onto_the_midpoint_evaluates_it_once_and_interpolation_is_exact_for_a_quadratic_inverse():
    """On ``sqrt(x) - 1/2`` over ``[0, 1]``, the first step lands on the midpoint 0.5, which is evaluated once, and the
    second step, an inverse quadratic interpolation, lands on the root 0.25 up to rounding, because the inverse
    function ``(y + 1/2)^2`` is quadratic."""
    # --- act --------------------------
    result = SteffenBrent().solve(
        lambda x: math.sqrt(x) - 0.5, 0.0, 1.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values[:3] == (0.0, 1.0, 0.5)
    assert result.evaluated_x_values[3] == pytest.approx(0.25, abs=1e-16)


def test_the_interval_does_not_always_halve():
    """On ``1 - 11 * exp(-24 * x)`` over ``[0, 1]``, the first step evaluates ``s`` near 0.91 and the midpoint 0.5;
    ``f(0.5)`` has the sign of ``f(s)``, so the interval keeps ``[0, s]``, 91 % of its width, and the next x-value
    lies below 0.5."""
    # --- act --------------------------
    result = SteffenBrent().solve(_steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    s, m, next_x = result.evaluated_x_values[2:5]
    assert s == pytest.approx(0.91, abs=0.01)
    assert m == 0.5
    assert next_x < 0.5


def test_equal_function_values_at_b_and_b_prev_force_a_bisection():
    """On ``1 - 11 * exp(-24 * x)`` over ``[0, 1]``, the swap at the end of an iteration, which keeps the smaller
    ``|f|`` in ``b``, makes ``b`` equal ``b_prev`` in several iterations, where the secant of the paper's Algorithm 2
    divides 0 by 0; `SteffenBrent` bisects there, and returns a root within ``xtol``."""
    # --- act --------------------------
    result = SteffenBrent().solve(_steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - math.log(11.0) / 24.0) <= 1e-10


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `SteffenBrent` returns an evaluated point
    within ``xtol`` of the root."""
    # --- act --------------------------
    result = SteffenBrent().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_to_its_root():
    """On ``x^9`` over ``[-1, 4]``, where interpolation converges slowly, `SteffenBrent` still returns a root within
    ``xtol``."""
    # --- act --------------------------
    result = SteffenBrent().solve(lambda x: x**9, -1.0, 4.0, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x) <= 1e-10


def test_an_exact_zero_ends_the_solve_without_evaluating_the_midpoint():
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = SteffenBrent().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`SteffenBrent` is named ``steffen_brent``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = SteffenBrent().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (SteffenBrent.name, SteffenBrent.version) == ("steffen_brent", 1)
    assert result.flop_counts.total_count() > 0
