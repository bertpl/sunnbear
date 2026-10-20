"""These tests assert that both variants of `Brent` converge to a simple root and to a multiple root."""

import pytest

from sunnbear.solvers import Bisection, Brent, BrentVariant, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES, ninth_power


@pytest.mark.parametrize("variant", BrentVariant)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root(f, a, b, root, variant):
    """Both variants of `Brent` return an x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`."""
    # --- act --------------------------
    result = Brent(variant=variant).solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10


@pytest.mark.parametrize("variant", BrentVariant)
def test_a_multiple_root_converges_within_3_times_the_evaluations_of_bisection(variant):
    """On `ninth_power` over ``[-1, 4]``, where interpolation converges slowly, both variants of `Brent` still converge
    within ``xtol``, with at most 3 times the evaluations of bisection."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    brent_result = Brent(variant=variant).solve(ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)
    bisection_result = Bisection().solve(ninth_power, -1.0, 4.0, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert brent_result.status is SolveStatus.CONVERGED
    assert abs(brent_result.x) <= xtol
    assert brent_result.n_fevals <= 3 * bisection_result.n_fevals
