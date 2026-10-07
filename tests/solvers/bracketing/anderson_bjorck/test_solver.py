"""These tests assert that `AndersonBjorck` scales down the function value of a bound that the interval keeps twice in
a row, by the factor ``1 - f_new / f_previous`` or by 0.5 where that factor is not positive, which ends regula falsi's
stall."""

import pytest

from sunnbear.solvers import AndersonBjorck, RegulaFalsi, SolveStatus
from tests.solvers.example_functions import (
    CUBIC_ROOT,
    STEEP_EXPONENTIAL_ROOT,
    cubic,
    decreasing_cubic,
    steep_exponential,
)


def _cubic_with_a_local_maximum(x: float) -> float:
    """Return ``x^3 - 2x + 2``, whose root is near -1.77; between the root and 0, f has a local maximum of about 3.09
    near -0.82, above f(0) = 2, so the first iterates from ``[-3, 0]``, which land in that range, raise ``|f|``."""
    return x**3 - 2.0 * x + 2.0


# ==================================================================================================
#  The modified step
# ==================================================================================================
@pytest.mark.parametrize(
    "f", [lambda x: x - 0.3, lambda x: 0.3 - x]
)  # The 2 functions cover both interval orientations.
def test_a_linear_function_is_solved_in_one_step(f):
    """On a straight line, the first chord lands on the root, so `AndersonBjorck` converges after the 2 bound
    evaluations and 1 iterate."""
    # --- act --------------------------
    result = AndersonBjorck().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.3, SolveStatus.CONVERGED, 3)


def test_the_first_2_steps_are_regula_falsi_and_the_third_scales_the_retained_f():
    """On the convex cubic, `AndersonBjorck`:

    - starts as regula falsi;
    - scales the value of the bound that it keeps again by ``1 - f_new / f_previous``;
    - drops the scaling once an iterate replaces that bound.
    """
    # --- arrange ----------------------
    a, b = 1.0, 2.0
    fa, fb = cubic(a), cubic(b)

    # --- act --------------------------
    history = AndersonBjorck().solve(cubic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, f2), (x3, f3), (x4, _) = history[2:6]
    assert x1 == (a * fb - b * fa) / (fb - fa)
    # f1 < 0, so x1 replaced the lower bound; the upper bound is kept for the first time, at its own value.
    assert f1 < 0.0
    assert x2 == (x1 * fb - b * f1) / (fb - f1)
    # f2 < 0 too, so x2 replaced x1 and the upper bound is kept a second time: its value is scaled.
    assert f2 < 0.0
    scaled_fb = (1.0 - f2 / f1) * fb
    assert x3 == (x2 * scaled_fb - b * f2) / (scaled_fb - f2)
    # f3 > 0, so x3 replaced the upper bound, and x2 is the retained bound, at its own value.
    assert f3 > 0.0
    assert x4 == (x2 * f3 - x3 * f2) / (f3 - f2)


def test_the_factor_falls_back_to_0_5_when_an_iterate_does_not_reduce_abs_f():
    """On `_cubic_with_a_local_maximum`, the first 2 iterates raise ``|f|``, so ``1 - f_new / f_previous`` is negative
    both times and `AndersonBjorck` halves the retained value instead."""
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
    # iterate (the default of AndersonBjorckState.newest_bound), so the factor 1 - f1 / fb is negative.
    assert f1 > fb > 0.0
    assert x2 == (a * f1 - x1 * (0.5 * fa)) / (f1 - 0.5 * fa)
    # f2 > f1 > 0, so 1 - f2 / f1 is negative too, and the retained value is halved again.
    assert f2 > f1
    assert x3 == (a * f2 - x2 * (0.25 * fa)) / (f2 - 0.25 * fa)


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # The 2 functions cover both interval orientations.
def test_a_convex_function_converges_where_regula_falsi_stalls(f):
    """On `cubic` in both interval orientations, regula falsi exhausts its budget, while Anderson-Björck converges
    well within it."""
    # --- act --------------------------
    regula_falsi_result = RegulaFalsi().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)
    anderson_bjorck_result = AndersonBjorck().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)

    # --- assert -----------------------
    assert regula_falsi_result.status is SolveStatus.MAX_FEVALS
    assert anderson_bjorck_result.status is SolveStatus.CONVERGED
    assert abs(anderson_bjorck_result.x - CUBIC_ROOT) <= 1e-9
    assert anderson_bjorck_result.n_fevals <= 15


# ==================================================================================================
#  Slow progress
# ==================================================================================================
def test_a_function_that_is_nearly_flat_on_1_side_of_the_root_takes_over_200_evaluations():
    """On `steep_exponential` over ``[0, 1]``, which is nearly flat left of the root, `AndersonBjorck` converges only
    after more than 200 evaluations, the slow progress that the class docstring describes."""
    # --- act --------------------------
    result = AndersonBjorck().solve(steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=1000)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - STEEP_EXPONENTIAL_ROOT) <= 1e-10
    assert result.n_fevals > 200


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`AndersonBjorck` is named ``anderson_bjorck``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = AndersonBjorck().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (AndersonBjorck.name, AndersonBjorck.version) == ("anderson_bjorck", 1)
    assert result.flop_counts.total_count() > 0
