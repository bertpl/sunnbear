"""These tests assert that the individual steps of `AndersonBjorck` follow its algorithm."""

import pytest

from sunnbear.solvers import AndersonBjorck, SolveStatus
from tests.solvers.example_functions import cubic


def _cubic_with_a_local_maximum(x: float) -> float:
    """Return ``x^3 - 2x + 2``, whose root is near -1.77; between the root and 0, f has a local maximum of about 3.09
    near -0.82, above f(0) = 2, so the first iterates from ``[-3, 0]``, which land in that range, raise ``|f|``."""
    return x**3 - 2.0 * x + 2.0


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.25, lambda x: 0.25 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first chord lands on the root, so `AndersonBjorck` converges after the 2 bound
    evaluations and 1 iterate.

    The root 0.25 is a power of 2, so the paper's step computes it without rounding, and the test can compare the
    result exactly.
    """
    # --- act --------------------------
    result = AndersonBjorck().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


def test_the_first_2_steps_are_regula_falsi_and_the_third_scales_the_retained_f():
    """On `cubic`, `AndersonBjorck` starts as regula falsi, scales the value of an interval bound by the ratio of 2
    chord slopes once it has kept that bound for 2 steps in a row, and drops that scaling once an iterate replaces
    the scaled bound.

    Each step takes the form of `chord_zero`, and each factor the form of the paper's ALGOL procedure.
    """
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = AndersonBjorck().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, f3), (x4, _) = history[2:6]
    # Before the first iterate, the upper bound counts as the most recent iterate.
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    assert x2 == (b * f1 - x1 * fb) / (f1 - fb)
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is scaled by the slope from
    # x1 to x2, divided by the slope of the chord that produced x2.
    assert f2 < 0.0
    scaled_fb = (((f2 - f1) / (x2 - x1)) / ((f1 - fb) / (x1 - b))) * fb
    assert x3 == (b * f2 - x2 * scaled_fb) / (f2 - scaled_fb)
    # f3 > 0, so x3 replaced the upper bound, and x2 is the retained bound, at its own value.
    assert f3 > 0.0
    assert x4 == (x2 * f3 - x3 * f2) / (f3 - f2)


def test_the_factor_falls_back_to_0_5_when_an_iterate_does_not_reduce_abs_f():
    """On `_cubic_with_a_local_maximum`, the first 2 iterates raise ``|f|``, so the ratio of slopes is negative both
    times and `AndersonBjorck` halves the retained value instead."""
    # --- arrange ----------------------
    a, b = -3.0, 0.0
    fa, fb = _cubic_with_a_local_maximum(a), _cubic_with_a_local_maximum(b)

    # --- act --------------------------
    history = (
        AndersonBjorck()
        .solve(_cubic_with_a_local_maximum, a, b, xtol=1e-9, max_fevals=60, history_enabled=True)
        .history
    )

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, _) = history[2:5]
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 > fb > 0, so x1 replaced the upper bound; before the first iterate, the upper bound counts as the previous
    # iterate, and the slope from b to x1 has the sign opposite to the chord's, so the factor is negative.
    assert f1 > fb > 0.0
    assert x2 == (a * f1 - x1 * (0.5 * fa)) / (f1 - 0.5 * fa)
    # f2 > f1 > 0, so the factor, which equals 1 - f2 / f1 in exact arithmetic, is negative too, and the retained
    # value is halved again.
    assert f2 > f1
    assert x3 == (a * f2 - x2 * (0.25 * fa)) / (f2 - 0.25 * fa)


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.999999, lambda x: 0.999999 - x]
)  # The 2 functions cover both interval orientations.
def test_a_chord_zero_within_xtol_of_the_upper_bound_is_replaced_by_a_step_of_delta_below_it(f):
    """On a straight line whose root lies 1e-6 below the upper bound, the first chord's zero lies within ``xtol = 1e-3``
    of the upper bound, which counts as the most recent iterate before the first iterate.

    `AndersonBjorck` therefore evaluates ``xtol`` below the upper bound, toward the retained lower bound. That step
    crosses the root, so the interval is ``xtol`` wide and the solve returns its midpoint.
    """
    # --- act --------------------------
    result = AndersonBjorck().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values == (0.0, 1.0, 1.0 - 1e-3)
    assert (result.x, result.status) == (0.5 * ((1.0 - 1e-3) + 1.0), SolveStatus.CONVERGED)


def test_a_chord_zero_within_xtol_of_the_lower_bound_is_replaced_by_a_step_of_delta_above_it():
    """On `cubic` over ``[1, 2]`` at ``xtol = 1e-3``, the 3rd and 4th iterates lie on opposite sides of the root, and
    the chord through them has its zero within ``xtol`` of the 4th, which holds the lower bound.

    `AndersonBjorck` therefore evaluates ``xtol`` above the 4th iterate, toward the retained upper bound, the 3rd
    iterate. That step crosses the root and ends the solve.
    """
    # --- arrange ----------------------
    xtol = 1e-3

    # --- act --------------------------
    result = AndersonBjorck().solve(cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    (x3, f3), (x4, f4), (x5, f5) = result.history[4:7]
    # x4 replaced the retained bound, so x3 is the retained bound, at its own value.
    assert f3 > 0.0 > f4
    assert abs((x3 * f4 - x4 * f3) / (f4 - f3) - x4) < xtol
    assert x5 == x4 + xtol
    assert f5 > 0.0
    assert result.n_fevals == 7
