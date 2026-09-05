import pytest

from sunnbear.solvers import RegulaFalsi, SolveStatus

from .example_functions import calibrated_cubic, cube_minus_two


@pytest.mark.parametrize("f", [lambda x: 2.0 * x - 0.5, lambda x: 0.5 - 2.0 * x])  # increasing and decreasing
def test_linear_function_is_solved_in_one_step(f):
    """The secant point of a linear function is its root, so the zero-endpoint criterion ends the solve."""
    # --- act --------------------------
    result = RegulaFalsi().solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.x, result.n_iters, result.n_fevals) == (SolveStatus.CONVERGED, 0.25, 1, 3)


def test_curved_function_exhausts_the_budget_with_the_moving_endpoint_at_the_root():
    """Endpoint retention keeps the bracket wide, so the budget is exhausted although the iterates have converged."""
    # --- act --------------------------
    result = RegulaFalsi().solve(cube_minus_two, 0.0, 2.0, xtol=1e-8, max_fevals=60, record_history=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert (result.n_fevals, result.n_iters) == (60, 58)
    assert abs(result.history[-1][0] - 2.0 ** (1 / 3)) < 1e-9  # The last secant point sits on the root.
    assert result.x != pytest.approx(2.0 ** (1 / 3), abs=1e-3)  # The reported x is the still-wide bracket's midpoint.


def test_catalog_function_exhausts_the_budget():
    """A compiled catalog function, curved on its bracket, exhausts the budget with its flops counted."""
    # --- arrange ----------------------
    test_function = calibrated_cubic()
    f = test_function.build_x_fun(1.0)

    # --- act --------------------------
    result = RegulaFalsi().solve(f, test_function.a, test_function.b, xtol=1e-9, max_fevals=40)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 40
    assert result.flop_counts.total_count() > 0
