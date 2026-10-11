"""These tests assert that `AndersonBjorck` converges on a convex function, where `RegulaFalsi` stalls, and that it
returns an evaluated x-value within ``xtol`` of the root."""

import pytest

from sunnbear.solvers import AndersonBjorck, RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


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


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # The 2 functions cover both interval orientations.
def test_the_solve_returns_an_evaluated_x_value_within_xtol_of_the_root(f):
    """`AndersonBjorck` returns an evaluated x-value within ``xtol`` of the root of `cubic` and `decreasing_cubic`."""
    # --- act --------------------------
    result = AndersonBjorck().solve(f, 1.0, 2.0, xtol=1e-3, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x in [x for x, _ in result.history]
    assert abs(result.x - CUBIC_ROOT) <= 1e-3
