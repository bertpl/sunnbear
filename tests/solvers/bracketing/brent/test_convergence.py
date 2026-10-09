"""These tests assert that `Brent` converges to a simple root and to a multiple root."""

import pytest

from sunnbear.solvers import Bisection, Brent, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `Brent` returns an evaluated point within
    ``xtol`` of the root."""
    # --- act --------------------------
    result = Brent().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_within_3_times_the_evaluations_of_bisection():
    """On ``x^9`` over ``[-1, 4]``, where interpolation converges slowly, `Brent` still converges within ``xtol``,
    with at most 3 times the evaluations of bisection."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    brent_result = Brent().solve(lambda x: x**9, -1.0, 4.0, xtol=xtol, max_fevals=500)
    bisection_result = Bisection().solve(lambda x: x**9, -1.0, 4.0, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert brent_result.status is SolveStatus.CONVERGED
    assert abs(brent_result.x) <= xtol
    assert brent_result.n_fevals <= 3 * bisection_result.n_fevals
