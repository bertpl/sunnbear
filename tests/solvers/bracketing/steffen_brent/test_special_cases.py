"""These tests assert that an exact zero at a new x-value ends a `SteffenBrent` solve once that x-value is an interval
bound."""

import pytest

from sunnbear.solvers import SolveStatus, SteffenBrent


@pytest.mark.parametrize(
    "f",
    [
        pytest.param(lambda x: x - 0.25, id="increasing"),
        pytest.param(lambda x: 0.25 - x, id="decreasing"),
    ],
)
def test_an_exact_zero_ends_the_solve_after_the_midpoint_is_evaluated(f):
    """On a line over ``[0, 1]``, the first secant step lands on the root 0.25, where the function is exactly 0.

    As in Algorithm 2, a 0 at ``s`` does not have the sign of ``f(a)``, so the solve evaluates the midpoint 0.625 of
    ``a = 1`` and ``s``, which does not replace ``a``. ``s`` becomes the bound ``b``, and the stopping criterion then
    returns it after 4 evaluations. The 2 lines give ``f(a)`` either sign.
    """
    # --- act --------------------------
    result = SteffenBrent().solve(f, 0.0, 1.0, xtol=1e-10, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert (result.x, result.status) == (0.25, SolveStatus.CONVERGED)
    assert result.evaluated_x_values == (0.0, 1.0, 0.25, 0.625)
