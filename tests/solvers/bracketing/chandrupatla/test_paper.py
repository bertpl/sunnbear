"""These tests assert that `Chandrupatla` reproduces the evaluation counts of Table 2 of its paper."""

import math

import pytest

from sunnbear.solvers import Chandrupatla, SolveStatus
from tests.solvers.bracketing.chandrupatla.paper_functions import PAPER_FUNCTIONS


def _listing_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, set to 0 where ``|x| < 3.8e-4``, as the paper's BASIC
    listing does."""
    if abs(x) < 3.8e-4:
        return 0.0
    else:
        return x * math.exp(-(x**-2))


# `_LISTING_FUNCTIONS` holds the test functions of the paper's Table 1, keyed by their number in that table, with
# function 7 replaced by `_listing_function_7`, the version in the paper's BASIC listing.
_LISTING_FUNCTIONS = {**PAPER_FUNCTIONS, 7: _listing_function_7}

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


@pytest.mark.parametrize("function_number, a, b, n_fevals", _PAPER_TABLE_2)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(function_number, a, b, n_fevals):
    """On every row of the paper's Table 2, `Chandrupatla` evaluates exactly as often as the paper reports.

    The paper's absolute tolerance is 1e-5, and its relative tolerance of 1e-10 makes no difference to these counts,
    so the solver's ``xtol`` of 1e-5 reproduces them.
    """
    # --- act --------------------------
    result = Chandrupatla().solve(_LISTING_FUNCTIONS[function_number], float(a), float(b), xtol=1e-5, max_fevals=100)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_fevals)
