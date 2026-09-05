import pytest

from sunnbear.functions import FormulaRegistry
from sunnbear.solvers import RegulaFalsi, SolveStatus


def _cube_minus_two(x: float) -> float:
    return x**3 - 2.0


def test_linear_function_is_solved_in_one_step():
    """The secant point of a linear function is its root, so the zero-endpoint criterion ends the solve."""
    # --- act --------------------------
    result = RegulaFalsi().solve(lambda x: 2.0 * x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.x, result.n_iters, result.n_fevals) == (SolveStatus.CONVERGED, 0.25, 1, 3)


def test_curved_function_exhausts_the_budget_with_the_moving_endpoint_at_the_root():
    """Endpoint retention keeps the bracket wide, so the solve hits the budget although the iterates have converged."""
    # --- act --------------------------
    result = RegulaFalsi().solve(_cube_minus_two, 0.0, 2.0, xtol=1e-8, max_fevals=60, record_history=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert (result.n_fevals, result.n_iters) == (60, 58)
    assert abs(result.history[-1][0] - 2.0 ** (1 / 3)) < 1e-9  # The last secant point sits on the root.
    assert result.x != pytest.approx(2.0 ** (1 / 3), abs=1e-3)  # The reported x is the still-wide bracket's midpoint.


def test_decreasing_function_is_handled_by_sign_normalization():
    # --- act --------------------------
    result = RegulaFalsi().solve(lambda x: 0.5 - 2.0 * x, 0.0, 1.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.x) == (SolveStatus.CONVERGED, 0.25)


def test_catalog_function_runs_into_the_budget():
    """A compiled catalog function, curved on its bracket, runs the MAX_FEVALS outcome end to end."""
    # --- arrange ----------------------
    test_function = FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0)
    f = test_function.build_x_fun(1.0)

    # --- act --------------------------
    result = RegulaFalsi().solve(f, test_function.a, test_function.b, xtol=1e-9, max_fevals=40)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 40
    assert result.flop_counts.total_count() > 0
