"""These tests assert that `Secant` converges on a smooth function, and returns the next x-value without evaluating
it."""

from sunnbear.solvers import Secant, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic


def test_the_returned_point_is_the_next_point_without_its_evaluation():
    """`Secant` stops once the step from the newest point is at most ``xtol``, and returns the next point without
    evaluating it."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    evaluated_x_values = result.evaluated_x_values
    assert result.status is SolveStatus.CONVERGED
    assert result.x not in evaluated_x_values
    assert abs(result.x - evaluated_x_values[-1]) <= 1e-10
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


def test_a_smooth_function_converges_in_few_evaluations():
    """On the cubic, near which the secant method converges faster than linearly, `Secant` reaches ``xtol = 1e-10``
    within 10 evaluations."""
    # --- act --------------------------
    result = Secant().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals <= 10
