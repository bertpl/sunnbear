"""These tests assert that `Pegasus` converges on a convex function, where `RegulaFalsi` stalls."""

import pytest

from sunnbear.solvers import Pegasus, RegulaFalsi, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])  # The 2 functions cover both interval orientations.
def test_a_convex_function_converges_where_regula_falsi_stalls(f):
    """On `cubic` in both interval orientations, regula falsi exhausts its budget, while Pegasus converges well
    within it."""
    # --- act --------------------------
    regula_falsi_result = RegulaFalsi().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)
    pegasus_result = Pegasus().solve(f, 1.0, 2.0, xtol=1e-9, max_fevals=60)

    # --- assert -----------------------
    assert regula_falsi_result.status is SolveStatus.MAX_FEVALS
    assert pegasus_result.status is SolveStatus.CONVERGED
    assert abs(pegasus_result.x - CUBIC_ROOT) <= 1e-9
    assert pegasus_result.n_fevals <= 15
