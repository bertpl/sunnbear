"""These tests assert that `CARF` reproduces Tables 3 and 4 of its paper, and that the rows of Table 4 that it does
not reproduce still converge."""

import pytest

from sunnbear.solvers import CARF, SolveStatus
from tests.solvers.bracketing.chandrupatla.paper_functions import PAPER_FUNCTIONS as CHANDRUPATLA_FUNCTIONS
from tests.solvers.bracketing.toms748.paper_problems import PAPER_PROBLEMS as TOMS748_PROBLEMS

# Each row of the paper's Table 4, on Chandrupatla's test functions, holds:
# - the function number;
# - the 2 interval bounds;
# - CARF's evaluation count.
_PAPER_TABLE_4 = [
    (1, 2, 3, 7),
    (1, 1, 10, 9),
    (1, 1, 100, 10),
    (1, -1e4, 1e4, 23),
    (1, -1e10, 1e10, 10),
    (2, 0.5, 1.51, 10),
    (2, 1e-4, 1e4, 19),
    (2, 1e-6, 1e6, 58),
    (2, 1e-10, 1e10, 46),
    (2, 1e-12, 1e12, 57),
    (3, 0, 5, 28),
    (3, -10, 10, 32),
    (3, -1e4, 1e4, 42),
    (3, -1e6, 1e6, 45),
    (3, -1e10, 1e10, 47),
    (4, 0, 5, 18),
    (4, -10, 10, 23),
    (4, -1e4, 1e4, 39),
    (4, -1e6, 1e6, 39),
    (4, -1e10, 1e10, 53),
    (5, -1, 4, 8),
    (5, -2, 5, 16),
    (5, -1, 10, 13),
    (5, -5, 50, 16),
    (5, -10, 100, 22),
    (6, -1, 4, 8),
    (6, -2, 5, 13),
    (6, -1, 10, 3),
    (6, -5, 50, 5),
    (6, -10, 100, 8),
    (7, -1, 4, 9),
    (7, -2, 5, 7),
    (7, -1, 10, 3),
    (7, -5, 50, 13),
    (7, -10, 100, 11),
    (8, 2e-4, 2, 12),
    (8, 2e-4, 3, 13),
    (8, 2e-4, 9, 11),
    (8, 2e-4, 27, 19),
    (8, 2e-4, 81, 26),
    (9, 2e-4, 1, 7),
    (9, 2e-4, 3, 10),
    (9, 2e-4, 9, 8),
    (9, 2e-4, 27, 10),
    (9, 2e-4, 81, 12),
]

# `_UNREPRODUCED_ROWS` holds the rows of `_PAPER_TABLE_4` whose count `CARF` does not reproduce, keyed by function
# number and interval:
# - some of the wide intervals of functions 1 to 4, where ``h``, the scaled function value at ``t`` that `CARF`'s
#   docstring defines, often lies within rounding error of 0 or 1, the limits that choose the kind of step, so the
#   count depends on how the paper's code computes the quadratic's root and the power step;
# - rows (8, 2e-4, 2) and (9, 2e-4, 1), whose last step lands on the other side of the root, or exactly on it, so a
#   1-ulp difference in that step changes the count.
_UNREPRODUCED_ROWS = {
    (1, -1e4, 1e4),
    (1, -1e10, 1e10),
    (2, 1e-4, 1e4),
    (2, 1e-10, 1e10),
    (2, 1e-12, 1e12),
    (3, -1e6, 1e6),
    (3, -1e10, 1e10),
    (4, -1e4, 1e4),
    (4, -1e6, 1e6),
    (4, -1e10, 1e10),
    (8, 2e-4, 2),
    (9, 2e-4, 1),
}


@pytest.mark.parametrize(
    "function_number, a, b, n_fevals", [row for row in _PAPER_TABLE_4 if row[:3] not in _UNREPRODUCED_ROWS]
)
def test_the_evaluation_counts_of_table_4_of_the_paper_are_reproduced(function_number, a, b, n_fevals):
    """With the paper's tolerances ``eps1 = 1e-15`` and ``eps2 = 1e-12``, `CARF` evaluates exactly as often as Table 4
    reports, on every row outside `_UNREPRODUCED_ROWS`."""
    # --- act --------------------------
    result = _CARFWithPaperTolerances(eps1=1e-15, eps2=1e-12).solve(
        CHANDRUPATLA_FUNCTIONS[function_number], float(a), float(b), xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_fevals)


@pytest.mark.parametrize("function_number, a, b", sorted(_UNREPRODUCED_ROWS))
def test_the_unreproduced_rows_of_table_4_still_converge(function_number, a, b):
    """On the rows in `_UNREPRODUCED_ROWS`, `CARF` still converges with the paper's tolerances."""
    # --- act --------------------------
    result = _CARFWithPaperTolerances(eps1=1e-15, eps2=1e-12).solve(
        CHANDRUPATLA_FUNCTIONS[function_number], float(a), float(b), xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED


@pytest.mark.parametrize("eps2, paper_total", [(1e-7, 2456), (1e-10, 2457), (1e-15, 2481)])
def test_the_total_evaluation_count_lies_within_1_5_percent_of_the_papers_table_3(eps2, paper_total):
    """Over the test problems of Algorithm 748, the total evaluation count lies within 1.5 % of the paper's Table
    3, at each of that table's tolerances ``eps2``, with ``eps1 = 1e-15`` as in the paper's Table 4."""
    # --- arrange / act ----------------
    total = sum(
        _CARFWithPaperTolerances(eps1=1e-15, eps2=eps2)
        .solve(problem.f, *problem.interval, xtol=0.0, max_fevals=300)
        .n_fevals
        for problem in TOMS748_PROBLEMS
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.015 * paper_total


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _CARFWithPaperTolerances(CARF):
    """`_CARFWithPaperTolerances` is `CARF` with the paper's stop test and its tolerances ``eps1`` and ``eps2``."""

    def __init__(self, *, eps1: float, eps2: float) -> None:
        """Configure the paper's tolerance ``eps1`` on ``|f|`` and on ``|t|``, and its absolute tolerance ``eps2``."""
        super().__init__()
        self._eps1 = eps1
        self._eps2 = eps2

    def _is_converged(self, t: float, ft: float, active_width: float, xtol: float) -> bool:
        """Return whether ``|f(t)| < eps1``, ``f(t) = 0``, or the active bracket is narrower than
        ``eps2 + |t| * eps1``, ignoring ``xtol``."""
        return abs(ft) < self._eps1 or ft == 0.0 or active_width < self._eps2 + abs(t) * self._eps1
