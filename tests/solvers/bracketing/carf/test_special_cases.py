"""These tests assert how `CARF` handles these special cases:

- an exact zero;
- function values near the root so small that the quadratic's formula could divide by 0;
- an ``xtol`` so small that the clipped x-values round onto the interval bounds.
"""

import math

from sunnbear._core.benchmark.protocol.tolerances import MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND
from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import CARF, SolveStatus


def test_an_exact_zero_ends_the_solve_at_that_point():
    """On a straight line, the secant's zero is the root, so the first x-value has a function value of exactly 0, and
    the solve returns it after 3 evaluations."""
    # --- act --------------------------
    result = CARF().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


def test_tiny_function_values_near_the_root_of_x_to_the_19th_still_converge():
    """On ``x^19`` over ``[-1, 4]`` at the benchmark's smallest allowed ``xtol``, where the function values near the
    root fall below 1e-180, `CARF` converges to the root."""
    # --- arrange ----------------------
    xtol = MIN_ALLOWED_XTOL_IN_FLOAT64_EPS_OF_MAX_ABS_INTERVAL_BOUND * FLOAT64_EPS * 4.0

    # --- act --------------------------
    result = CARF().solve(lambda x: x**19, -1.0, 4.0, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x) <= xtol


def test_an_x_value_on_an_interval_bound_ends_the_solve_by_the_evaluation_budget():
    """At ``xtol = 5e-16``, so that the stopping width ``2*xtol`` is about 2 ulps at the root of ``(x - 3)^3`` over
    ``[0, 5]``, the solve ends as ``MAX_FEVALS`` within 1 ulp of the root: the clipped x-values round onto the interval
    bounds, where the quadratic is not defined, and `CARF` takes the zero of the secant through the 2 bounds."""
    # --- act --------------------------
    result = CARF().solve(lambda x: (x - 3.0) ** 3, 0.0, 5.0, xtol=5e-16, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert abs(result.x - 3.0) <= math.ulp(3.0)
