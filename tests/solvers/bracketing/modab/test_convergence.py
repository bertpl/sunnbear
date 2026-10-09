"""These tests assert that `ModAB` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import ModAB, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root):
    """`ModAB` returns an x-value within ``xtol`` of the root on an increasing function (`cubic`), a decreasing
    function (`decreasing_cubic`), and a function with a multiple root (`ninth_power` over ``[-1, 4]``); on
    `ninth_power`, `ModAB` never switches to Anderson-Björck mode, because the function never comes close enough to a
    straight line."""
    # --- act --------------------------
    result = ModAB().solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
