"""These tests assert how `AndersonBjorck` handles a function that is nearly flat on 1 side of the root, and a step
that rounds onto the most recent iterate."""

from sunnbear.solvers import AndersonBjorck, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, STEEP_EXPONENTIAL_ROOT, cubic, steep_exponential


def test_a_function_that_is_nearly_flat_on_1_side_of_the_root_takes_over_200_evaluations():
    """On `steep_exponential` over ``[0, 1]``, which is nearly flat left of the root, `AndersonBjorck` converges only
    after more than 200 evaluations, the slow progress that the class docstring describes."""
    # --- act --------------------------
    result = AndersonBjorck().solve(steep_exponential, 0.0, 1.0, xtol=1e-10, max_fevals=1000)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - STEEP_EXPONENTIAL_ROOT) <= 1e-10
    assert result.n_fevals > 200


def test_a_step_that_rounds_onto_the_most_recent_iterate_takes_the_factor_0_5():
    """On `cubic` over ``[1, 2]``, the 7th iterate lies within rounding error of the root while the retained bound is
    still far from it.

    The next step rounds onto the 7th iterate, so the slope from the previous to the new iterate is ``0 / 0``; the
    factor 0.5 then moves the following step away from the 7th iterate, and the solve converges.
    """
    # --- act --------------------------
    result = AndersonBjorck().solve(cubic, 1.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    # The history starts with the 2 interval bounds, so index 8 holds the 7th iterate.
    x_values = [x for x, _ in result.history]
    assert x_values[8] == x_values[9] != x_values[10]
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-9
