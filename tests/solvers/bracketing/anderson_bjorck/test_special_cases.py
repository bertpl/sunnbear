"""These tests assert how `AndersonBjorck` handles a function that is nearly flat on 1 side of the root, and a step
that rounds onto the most recent iterate."""

from sunnbear.solvers import AndersonBjorck, SolveStatus
from tests.solvers.example_functions import STEEP_EXPONENTIAL_ROOT, cubic, steep_exponential


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
    """On `cubic` over ``[1, 2]`` at ``xtol = 0``, where the step of delta never applies, the 7th iterate lies within
    rounding error of the root while the retained bound is still far from it.

    The next 2 steps round onto the 7th iterate, so the slope from the previous to the new iterate is ``0 / 0`` each
    time; the factor 0.5, taken at each of them, then moves the following step away from the 7th iterate.
    """
    # --- act --------------------------
    result = AndersonBjorck().solve(cubic, 1.0, 2.0, xtol=0.0, max_fevals=12, history_enabled=True)

    # --- assert -----------------------
    # The history starts with the 2 interval bounds, so index 8 holds the 7th iterate.
    x_values = result.evaluated_x_values
    assert x_values[8] == x_values[9] == x_values[10] != x_values[11]
    # At xtol = 0, the solve runs until its budget is spent; a division of 0 by 0 would have ended it as SOLVER_ERROR.
    assert result.status is SolveStatus.MAX_FEVALS
