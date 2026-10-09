"""These tests assert that `CARF` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import CARF, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root):
    """`CARF` returns an x-value within ``xtol`` of the root on each function of `CONVERGENCE_TEST_CASES`; on
    `ninth_power`, the multiple root makes `CARF` take power steps."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
