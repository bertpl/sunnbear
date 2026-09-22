"""`Bisection` is pinned to its exact evaluation count, since the benchmark derives reference costs from it."""

import math

import pytest

from sunnbear.solvers import Bisection, SolveStatus


def _cubic(x: float) -> float:
    return x**3 - x - 1.0  # 1 real root, near 1.3247


def _decreasing_cubic(x: float) -> float:
    return -_cubic(x)


ROOT = 1.324717957244746


# ==================================================================================================
#  Convergence and the exact evaluation count
# ==================================================================================================
@pytest.mark.parametrize("f", [_cubic, _decreasing_cubic])  # both orientations
@pytest.mark.parametrize("a, b, xtol", [(1.0, 2.0, 1e-3), (0.0, 4.0, 1e-8), (1.3, 1.4, 1e-12)])
def test_converges_within_xtol_with_the_exact_evaluation_count(f, a, b, xtol):
    # --- act / assert -----------------
    result = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)
    n_steps = math.ceil(math.log2((b - a) / (2.0 * xtol)))
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - ROOT) <= xtol
    assert result.n_fevals == n_steps + 2


def test_an_exact_midpoint_root_stops_early():
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


def test_running_out_of_budget_reports_the_last_interval_midpoint():
    # --- act --------------------------
    result = Bisection().solve(_cubic, 1.0, 2.0, xtol=1e-12, max_fevals=6)

    # --- assert -----------------------
    # After the 2 bound evaluations, 4 steps ran: [1, 2] became [1, 1.5], [1.25, 1.5], [1.25, 1.375], [1.3125, 1.375].
    assert (result.status, result.n_fevals, result.x) == (SolveStatus.MAX_FEVALS, 6, 1.34375)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    # --- act --------------------------
    result = Bisection().solve(_cubic, 1.0, 2.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert (Bisection.name, Bisection.version) == ("bisection", 1)
    assert result.flop_counts.total_count() > 0
    assert result.history is None
