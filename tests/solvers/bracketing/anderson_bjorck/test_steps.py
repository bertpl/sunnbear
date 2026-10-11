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

    Each step and each factor take the form of the paper's ALGOL procedure.
    """
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = AndersonBjorck().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, f3), (x4, _) = history[2:6]
    # Before the first iterate, the upper bound counts as the most recent iterate.
    slope = (fb - fa) / (b - a)
    assert x1 == b - fb / slope
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    slope = (f1 - fb) / (x1 - b)
    assert x2 == x1 - f1 / slope
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is scaled by the slope from
    # x1 to x2, divided by the slope of the chord that produced x2.
    assert f2 < 0.0
    scaled_fb = (((f2 - f1) / (x2 - x1)) / slope) * fb
    slope = (f2 - scaled_fb) / (x2 - b)
    assert x3 == x2 - f2 / slope
    # f3 > 0, so x3 replaced the upper bound, and x2 is the retained bound, at its own value.
    assert f3 > 0.0
    slope = (f3 - f2) / (x3 - x2)
    assert x4 == x3 - f3 / slope


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
    assert x1 == b - fb / ((fb - fa) / (b - a))
    # f1 > fb > 0, so x1 replaced the upper bound; before the first iterate, the upper bound counts as the previous
    # iterate (the default of AndersonBjorckState.newest_bound), and the slope from b to x1 has the sign opposite to
    # the chord's, so the factor is negative.
    assert f1 > fb > 0.0
    assert x2 == x1 - f1 / ((f1 - 0.5 * fa) / (x1 - a))
    # f2 > f1 > 0, so the factor, which equals 1 - f2 / f1 in exact arithmetic, is negative too, and the retained
    # value is halved again.
    assert f2 > f1
    assert x3 == x2 - f2 / ((f2 - 0.25 * fa) / (x2 - a))
