"""These tests assert that `SteffenBrent` converges to a simple root and to a multiple root."""

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root):
    """`SteffenBrent` returns an evaluated x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`."""
    # --- act --------------------------
    result = SteffenBrent().solve(f, a, b, xtol=1e-10, max_fevals=500, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
    assert result.x in result.evaluated_x_values
