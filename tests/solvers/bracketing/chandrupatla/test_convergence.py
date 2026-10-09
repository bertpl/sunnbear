"""These tests assert that `Chandrupatla` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import Chandrupatla, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `Chandrupatla` returns an evaluated point
    within ``xtol`` of the root."""
    # --- act --------------------------
    result = Chandrupatla().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values
