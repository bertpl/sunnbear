import math

import pytest

from sunnbear.functions import FormulaRegistry
from sunnbear.solvers import Bisection, SolveStatus


def _cube_minus_two(x: float) -> float:
    return x**3 - 2.0


@pytest.mark.parametrize("xtol", [1e-2, 1e-6, 1e-10])
def test_converges_within_xtol(xtol):
    # --- act --------------------------
    result = Bisection().solve(_cube_minus_two, 0.0, 2.0, xtol=xtol, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - 2.0 ** (1 / 3)) <= xtol


@pytest.mark.parametrize("a, b, xtol", [(0.0, 2.0, 1e-3), (-1.0, 1.5, 1e-7), (0.0, 1.0, 0.3)])
def test_iteration_and_evaluation_counts_follow_the_bracket_arithmetic(a, b, xtol):
    """Pins the iteration and evaluation counts of a bisection solve as functions of the bracket and xtol."""
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.7, a, b, xtol=xtol, max_fevals=100)

    # --- assert -----------------------
    assert result.n_iters == math.ceil(math.log2((b - a) / (2.0 * xtol)))
    assert result.n_fevals == result.n_iters + 2


def test_exact_zero_at_a_midpoint_stops_early_on_that_endpoint():
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 1.0, 0.0, 2.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert (result.x, result.n_iters, result.n_fevals) == (1.0, 1, 3)


def test_decreasing_function_is_handled_by_sign_normalization():
    # --- act --------------------------
    result = Bisection().solve(lambda x: 0.3 - x, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - 0.3) <= 1e-9


def test_budget_exhaustion_reports_the_last_bracket_midpoint():
    # --- act --------------------------
    result = Bisection().solve(_cube_minus_two, 0.0, 2.0, xtol=1e-12, max_fevals=6)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert (result.n_fevals, result.n_iters) == (6, 4)
    assert abs(result.x - 2.0 ** (1 / 3)) <= 2.0 / 2**4  # The estimate lies within the bracket left after 4 halvings.


def test_flops_and_history_are_recorded():
    # --- act --------------------------
    result = Bisection().solve(_cube_minus_two, 0.0, 2.0, xtol=1e-6, max_fevals=100, record_history=True)

    # --- assert -----------------------
    assert result.flop_counts.total_count() > 0
    assert len(result.history) == result.n_fevals
    assert (result.history[0][0], result.history[1][0]) == (0.0, 2.0)  # The endpoints come first, in order.


def test_solves_a_catalog_test_function():
    """End-to-end through the functions layer: a compiled formula body behind a plain f(x)."""
    # --- arrange ----------------------
    test_function = FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0)
    f = test_function.build_x_fun(1.0)

    # --- act --------------------------
    result = Bisection().solve(f, test_function.a, test_function.b, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(f(result.x)) < 1e-7
