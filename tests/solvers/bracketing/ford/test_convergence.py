"""These tests assert that every variant of `Ford` converges to a root of the example functions, except at a multiple
root."""

import pytest

from sunnbear.solvers import Ford, FordVariant, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES, ninth_power


@pytest.mark.parametrize("variant", FordVariant)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root_except_at_a_multiple_root(f, a, b, root, variant):
    """Every variant of `Ford` returns an x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`, except on `ninth_power`, where no variant converges within 500 evaluations.

    Ford (1997) assumes a simple root. Near the multiple root of `ninth_power`, every iterate lies on the same side of
    the root, below it, so the interval keeps its upper bound, 4, and stays wider than ``2*xtol``, while each iterate
    lies only about 8 to 10 % closer to the root than the one before.
    """
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    result = Ford(variant=variant).solve(f, a, b, xtol=xtol, max_fevals=500, history_enabled=True)

    # --- assert -----------------------
    if f is ninth_power:
        assert result.status is SolveStatus.MAX_FEVALS
        assert all(x < root for x in result.evaluated_x_values[2:])
    else:
        assert result.status is SolveStatus.CONVERGED
        assert abs(result.x - root) <= xtol
