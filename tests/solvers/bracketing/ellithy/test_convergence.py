"""These tests assert that every variant of `Ellithy` converges to a root of the example functions."""

import pytest

from sunnbear.solvers import Ellithy, EllithyVariant, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES


@pytest.mark.parametrize("variant", EllithyVariant)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root, variant):
    """Every variant returns an x-value within ``xtol`` of the root on each function of `CONVERGENCE_TEST_CASES`.

    On `ninth_power`, whose root is a multiple root, the bisection or trisection of each iteration still shrinks the
    interval to the stopping width.
    """
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    result = Ellithy(variant=variant).solve(f, a, b, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= xtol
