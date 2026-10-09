"""These tests assert that `TOMS748` converges to a root of the test functions."""

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("k", [1, 2])
@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f, k):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `TOMS748` returns a point within
    ``xtol`` of the root."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
