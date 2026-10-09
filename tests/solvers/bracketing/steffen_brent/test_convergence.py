"""These tests assert that `SteffenBrent` converges to a simple root and to a multiple root."""

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `SteffenBrent` returns an evaluated point
    within ``xtol`` of the root."""
    # --- act --------------------------
    result = SteffenBrent().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_to_its_root():
    """On ``x^9`` over ``[-1, 4]``, where interpolation converges slowly, `SteffenBrent` still returns a root within
    ``xtol``."""
    # --- act --------------------------
    result = SteffenBrent().solve(lambda x: x**9, -1.0, 4.0, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x) <= 1e-10
