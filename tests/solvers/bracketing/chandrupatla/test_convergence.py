"""These tests assert that `Chandrupatla` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import Chandrupatla, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root):
    """`Chandrupatla` returns an evaluated x-value within ``xtol`` of the root on an increasing function (`cubic`), a
    decreasing function (`decreasing_cubic`), and a function with a multiple root (`ninth_power` over ``[-1, 4]``)."""
    # --- act --------------------------
    result = Chandrupatla().solve(f, a, b, xtol=1e-10, max_fevals=500, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
    assert result.x in result.evaluated_x_values
