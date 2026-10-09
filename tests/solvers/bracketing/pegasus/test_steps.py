"""These tests assert that the individual steps of `Pegasus` follow its algorithm."""

import pytest

from sunnbear.solvers import Pegasus, SolveStatus
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first chord lands on the root, so `Pegasus` converges after the 2 bound evaluations
    and 1 iterate."""
    # --- act --------------------------
    result = Pegasus().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_the_first_2_steps_are_regula_falsi_and_later_steps_scale_the_retained_f():
    """On the convex cubic, Pegasus starts as regula falsi, then scales the value of the bound that it keeps again,
    each time by the factor ``f_previous / (f_previous + f_new)`` of the 2 most recent iterates."""
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = Pegasus().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, f3), (x4, _) = history[2:6]
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    assert x2 == (x1 * fb - b * f1) / (fb - f1)
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is scaled.
    assert f2 < 0.0
    scaled_fb = (f1 / (f1 + f2)) * fb
    assert x3 == (x2 * scaled_fb - b * f2) / (scaled_fb - f2)
    # f3 < 0 too: the scaled value is scaled again, by the factor of x2 and x3.
    assert f3 < 0.0
    scaled_fb = (f2 / (f2 + f3)) * scaled_fb
    assert x4 == (x3 * scaled_fb - b * f3) / (scaled_fb - f3)
