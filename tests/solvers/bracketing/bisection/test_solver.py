"""These tests assert `Bisection`'s exact evaluation count, which the benchmark takes as its reference cost."""

import math

import pytest

from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


# ==================================================================================================
#  Convergence and the exact evaluation count
# ==================================================================================================
@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # Exercises both interval orientations.
@pytest.mark.parametrize("a, b, xtol", [(1.0, 2.0, 1e-3), (0.0, 4.0, 1e-8), (1.3, 1.4, 1e-12)])
def test_converges_within_xtol_with_the_exact_evaluation_count(f, a, b, xtol):
    # --- arrange ----------------------
    n_steps_expected = math.ceil(math.log2((b - a) / (2.0 * xtol)))
    n_fevals_expected = n_steps_expected + 2

    # --- act --------------------------
    result = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= xtol
    assert result.n_fevals == n_fevals_expected


def test_an_exact_midpoint_root_stops_early():
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


def test_running_out_of_budget_reports_the_last_interval_midpoint():
    # --- act --------------------------
    result = Bisection().solve(cubic, 1.0, 2.0, xtol=1e-12, max_fevals=6)

    # --- assert -----------------------
    # After the 2 bound evaluations, 4 steps ran; the interval sequence:
    #   [1, 2], then [1, 1.5], then [1.25, 1.5], then [1.25, 1.375], then [1.3125, 1.375].
    assert (result.status, result.n_fevals, result.x) == (SolveStatus.MAX_FEVALS, 6, 1.34375)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    # --- act --------------------------
    result = Bisection().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert (Bisection.name, Bisection.version) == ("bisection", 1)
    assert result.flop_counts.total_count() > 0
    assert result.history is None
