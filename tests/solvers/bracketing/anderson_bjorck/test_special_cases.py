"""These tests assert that `AndersonBjorck` needs over 200 evaluations on a function that is nearly flat on 1 side of
the root."""

from sunnbear.solvers import AndersonBjorck, SolveStatus
from tests.solvers.example_functions import STEEP_EXPONENTIAL_ROOT, steep_exponential


def test_a_function_that_is_nearly_flat_on_1_side_of_the_root_takes_over_200_evaluations():
    """On `steep_exponential` over ``[0, 1]``, which is nearly flat left of the root, `AndersonBjorck` converges only
    after more than 200 evaluations, the slow progress that the class docstring describes."""
    # --- act --------------------------
    result = AndersonBjorck().solve(steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=1000)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - STEEP_EXPONENTIAL_ROOT) <= 1e-10
    assert result.n_fevals > 200
