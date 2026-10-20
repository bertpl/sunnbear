"""These tests assert that `ModAB` and `ModABSafeguarded` converge to a root of the test functions."""

import pytest

from sunnbear.solvers import ModAB, ModABSafeguarded, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("solver_cls", [ModAB, ModABSafeguarded], ids=lambda cls: cls.__name__)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root, solver_cls):
    """`ModAB` and `ModABSafeguarded` each return an x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`; on `ninth_power`, neither ever switches to Anderson-Björck mode, because the function
    never comes close enough to a straight line."""
    # --- act --------------------------
    result = solver_cls().solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
