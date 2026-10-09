"""These tests assert that `Brent` converges to a simple root and to a multiple root."""

import pytest

from sunnbear.solvers import Bisection, Brent, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic, ninth_power


@pytest.mark.parametrize(
    "f, a, b, root",
    [
        (cubic, 1.0, 2.0, CUBIC_ROOT),
        (decreasing_cubic, 1.0, 2.0, CUBIC_ROOT),
        (ninth_power, -1.0, 4.0, 0.0),
    ],
    ids=["cubic", "decreasing_cubic", "ninth_power"],
)
def test_a_function_converges_to_its_root(f, a, b, root):
    """On `cubic`, which increases, `decreasing_cubic`, which decreases, and `ninth_power` over ``[-1, 4]``, whose root
    is a multiple root, `Brent` returns an evaluated x-value within ``xtol`` of the root."""
    # --- act --------------------------
    result = Brent().solve(f, a, b, xtol=1e-10, max_fevals=500, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_a_multiple_root_converges_within_3_times_the_evaluations_of_bisection():
    """On `ninth_power` over ``[-1, 4]``, where interpolation converges slowly, `Brent` still converges within ``xtol``,
    with at most 3 times the evaluations of bisection."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    brent_result = Brent().solve(ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)
    bisection_result = Bisection().solve(ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert brent_result.status is SolveStatus.CONVERGED
    assert abs(brent_result.x) <= xtol
    assert brent_result.n_fevals <= 3 * bisection_result.n_fevals
