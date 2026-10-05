"""These tests assert that `Illinois` halves the value of a bound that the interval keeps twice in a row, which ends
regula falsi's stall."""

import pytest

from sunnbear.solvers import Illinois, RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


# ==================================================================================================
#  The modified step
# ==================================================================================================
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


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # The 2 functions cover both interval orientations.
def test_a_convex_function_converges_where_regula_falsi_stalls(f):
    """On `cubic` in both interval orientations, regula falsi exhausts its budget, while Illinois converges well
    within it."""
    # --- act --------------------------
    regula_falsi = RegulaFalsi().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)
    illinois = Illinois().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)

    # --- assert -----------------------
    assert regula_falsi.status is SolveStatus.MAX_FEVALS
    assert illinois.status is SolveStatus.CONVERGED
    assert abs(illinois.x - CUBIC_ROOT) <= 1e-9
    assert illinois.n_fevals <= 15


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Illinois` is named ``illinois``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Illinois().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Illinois.name, Illinois.version) == ("illinois", 1)
    assert result.flop_counts.total_count() > 0
