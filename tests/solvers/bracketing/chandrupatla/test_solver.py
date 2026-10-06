"""These tests assert that `Chandrupatla` reproduces the evaluation counts of Chandrupatla's paper, and stops within
``xtol`` of a root."""

import math

import pytest

from sunnbear.solvers import Chandrupatla, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


def _paper_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, set to 0 where ``|x| < 3.8e-4``."""
    if abs(x) < 3.8e-4:
        return 0.0
    else:
        return x * math.exp(-(x**-2))


def _paper_function_8(x: float) -> float:
    """Return the paper's function 8."""
    xi = 0.61489
    return -3062.0 * (1.0 - xi) * math.exp(-x) / (xi + (1.0 - xi) * math.exp(-x)) - 1013.0 + 1628.0 / x


# `_PAPER_FUNCTIONS` holds the test functions of the paper's Table 1, keyed by their number in that table.
_PAPER_FUNCTIONS = {
    1: lambda x: x**3 - 2.0 * x - 5.0,
    2: lambda x: 1.0 - 1.0 / x**2,
    3: lambda x: (x - 3.0) ** 3,
    4: lambda x: 6.0 * (x - 2.0) ** 5,
    5: lambda x: x**9,
    6: lambda x: x**19,
    7: _paper_function_7,
    8: _paper_function_8,
    9: lambda x: math.exp(x) - 2.0 - 0.01 / x**2 + 0.000002 / x**3,
}

# Each row of the paper's Table 2 holds:
# - the function number;
# - the 2 interval bounds;
# - the evaluation count of the paper's method.
_PAPER_TABLE_2 = [
    (1, 2, 3, 7),
    (1, 1, 10, 11),
    (1, 1, 100, 14),
    (1, -1e4, 1e4, 23),
    (1, -1e10, 1e10, 43),
    (2, 0.5, 1.51, 8),
    (2, 1e-4, 1e4, 22),
    (2, 1e-6, 1e6, 28),
    (2, 1e-10, 1e10, 41),
    (2, 1e-12, 1e12, 48),
    (3, 0, 5, 21),
    (3, -10, 10, 23),
    (3, -1e4, 1e4, 36),
    (3, -1e6, 1e6, 45),
    (3, -1e10, 1e10, 55),
    (4, 0, 5, 21),
    (4, -10, 10, 23),
    (4, -1e4, 1e4, 33),
    (4, -1e6, 1e6, 43),
    (4, -1e10, 1e10, 54),
    (5, -1, 4, 21),
    (5, -2, 5, 22),
    (5, -1, 10, 23),
    (5, -5, 50, 25),
    (5, -10, 100, 26),
    (6, -1, 4, 21),
    (6, -2, 5, 22),
    (6, -1, 10, 23),
    (6, -5, 50, 25),
    (6, -10, 100, 26),
    (7, -1, 4, 8),
    (7, -2, 5, 8),
    (7, -1, 10, 11),
    (7, -5, 50, 18),
    (7, -10, 100, 19),
    (8, 2e-4, 2, 9),
    (8, 2e-4, 3, 10),
    (8, 2e-4, 9, 11),
    (8, 2e-4, 27, 12),
    (8, 2e-4, 81, 14),
    (9, 2e-4, 1, 7),
    (9, 2e-4, 3, 8),
    (9, 2e-4, 9, 10),
    (9, 2e-4, 27, 11),
    (9, 2e-4, 81, 13),
]


# ==================================================================================================
#  The paper's results
# ==================================================================================================
@pytest.mark.parametrize("function_number, a, b, n_fevals", _PAPER_TABLE_2)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(function_number, a, b, n_fevals):
    """On every row of the paper's Table 2, `Chandrupatla` evaluates exactly as often as the paper reports.

    The paper's absolute tolerance is 1e-5, and its relative tolerance of 1e-10 makes no difference to these counts,
    so the solver's ``xtol`` of 1e-5 reproduces them.
    """
    # --- act --------------------------
    result = Chandrupatla().solve(_PAPER_FUNCTIONS[function_number], float(a), float(b), xtol=1e-5, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_fevals)


# ==================================================================================================
#  The steps
# ==================================================================================================
def test_the_first_step_is_a_bisection():
    """`Chandrupatla` starts with ``t = 0.5``, so its first point is the midpoint of the interval."""
    # --- act --------------------------
    result = Chandrupatla().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 1.5


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `Chandrupatla` returns an evaluated point
    within ``xtol`` of the root."""
    # --- act --------------------------
    result = Chandrupatla().solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
    assert result.x in result.evaluated_x_values


def test_an_exact_zero_ends_the_solve_at_that_point():
    """A midpoint that is exactly the root ends the solve after 3 evaluations, the 2 bounds and that midpoint."""
    # --- act --------------------------
    result = Chandrupatla().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Chandrupatla` has name ``chandrupatla`` and version 1, and its flop count includes its square roots."""
    # --- act --------------------------
    result = Chandrupatla().solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=40)

    # --- assert -----------------------
    assert (Chandrupatla.name, Chandrupatla.version) == ("chandrupatla", 1)
    assert result.flop_counts.SQRT > 0
