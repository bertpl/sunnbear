"""These tests assert that both variants of `ModAB` converge to a root of the test functions."""

import pytest

from sunnbear.solvers import ModAB, ModABVariant, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("variant", ModABVariant)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root, variant):
    """Both variants of `ModAB` return an x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`; on `ninth_power`, neither variant ever switches to Anderson-Björck mode, because the
    function never comes close enough to a straight line."""
    # --- act --------------------------
    result = ModAB(variant=variant).solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
