"""These tests assert that the individual steps of `Illinois` follow its algorithm."""

import pytest

from sunnbear.solvers import Illinois, SolveStatus
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first chord lands on the root, so `Illinois` converges after 3 evaluations without
    halving any value."""
    # --- act --------------------------
    result = Illinois().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_the_first_2_steps_are_regula_falsi_and_the_third_halves_the_retained_bound():
    """On the convex cubic, Illinois starts as regula falsi, then halves the value of the bound that it keeps again."""
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = Illinois().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, _) = history[2:5]
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    assert x2 == (x1 * fb - b * f1) / (fb - f1)
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is halved.
    assert f2 < 0.0
    assert x3 == (x2 * (0.5 * fb) - b * f2) / (0.5 * fb - f2)
