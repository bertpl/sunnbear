"""These tests assert that `CARF` reproduces the paper's Tables 3 and 4 as far as its reconstruction allows, takes the
steps that its docstring describes, and stops within ``xtol`` of a root."""

import pytest

from sunnbear.solvers import CARF, SolveStatus
from tests.solvers.bracketing.chandrupatla.paper_functions import PAPER_FUNCTIONS
from tests.solvers.bracketing.toms748.paper_problems import PAPER_PROBLEMS
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic, steep_exponential

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
# - the wide intervals of functions 1 to 4, where ``h`` often lies within rounding error of 0 or 1, the limits that
#   choose the kind of step, so the count depends on how the paper's code computes the quadratic's root and the power
#   step;
# - rows (8, 2e-4, 2) and (9, 2e-4, 1), whose last step lands on the other side of the root, or exactly on it: moving
#   that step's x-value by 1 ulp gives the paper's count of 7 for function 9.
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


# ==================================================================================================
#  The paper's results
# ==================================================================================================
@pytest.mark.parametrize(
    "function_number, a, b, n_fevals", [row for row in _PAPER_TABLE_4 if row[:3] not in _UNREPRODUCED_ROWS]
)
def test_the_evaluation_counts_of_table_4_of_the_paper_are_reproduced(function_number, a, b, n_fevals):
    """With the paper's tolerances ``eps1 = 1e-15`` and ``eps2 = 1e-12``, `CARF` evaluates exactly as often as Table 4
    reports, on every row outside `_UNREPRODUCED_ROWS`."""
    # --- act --------------------------
    result = _CARFWithPaperTolerances(eps1=1e-15, eps2=1e-12).solve(
        PAPER_FUNCTIONS[function_number], float(a), float(b), xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_fevals)


@pytest.mark.parametrize("function_number, a, b", sorted(_UNREPRODUCED_ROWS))
def test_the_unreproduced_rows_of_table_4_still_converge(function_number, a, b):
    """On the rows in `_UNREPRODUCED_ROWS`, `CARF` still converges with the paper's tolerances."""
    # --- act --------------------------
    result = _CARFWithPaperTolerances(eps1=1e-15, eps2=1e-12).solve(
        PAPER_FUNCTIONS[function_number], float(a), float(b), xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED


@pytest.mark.parametrize("eps2, paper_total", [(1e-7, 2456), (1e-10, 2457), (1e-15, 2481)])
def test_the_total_evaluation_count_lies_within_1_5_percent_of_the_papers_table_3(eps2, paper_total):
    """Over the test problems of Algorithm 748, the total evaluation count lies within 1.5 % of the paper's Table
    3, at each of its tolerances ``eps2``, with ``eps1 = 1e-15`` as in its Table 4."""
    # --- arrange / act ----------------
    total = sum(
        _CARFWithPaperTolerances(eps1=1e-15, eps2=eps2)
        .solve(problem.f, *problem.interval, xtol=0.0, max_fevals=300)
        .n_fevals
        for problem in PAPER_PROBLEMS
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.015 * paper_total


# ==================================================================================================
#  The steps
# ==================================================================================================
@pytest.mark.parametrize(
    "f, a, b, first_x",
    [(cubic, 1.0, 2.0, 1.0 + 1.0 / 6.0), (steep_exponential, 0.0, 1.0, 0.1)],
    ids=["chord_zero_inside", "chord_zero_clipped"],
)
def test_the_first_x_value_is_the_chord_zero_clipped_into_the_middle_80_percent(f, a, b, first_x):
    """The first x-value is the chord's zero, kept when it lies in the middle 80 % of the interval and clipped to its
    edge otherwise."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(first_x, abs=1e-15)


def test_an_exact_zero_ends_the_solve_at_that_point():
    """On a line, the first x-value, the chord's zero, is the root, where the function is exactly 0, and the solve
    returns it after 3 evaluations."""
    # --- act --------------------------
    result = CARF().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize(
    "f, a, b, root",
    [
        (cubic, 1.0, 2.0, CUBIC_ROOT),
        (decreasing_cubic, 1.0, 2.0, CUBIC_ROOT),
        (lambda x: x**9, -1.0, 4.0, 0.0),
    ],
    ids=["cubic", "decreasing_cubic", "multiple_root"],
)
def test_a_function_converges_to_its_root(f, a, b, root):
    """On `cubic`, which increases, `decreasing_cubic`, which decreases, and ``x^9`` over ``[-1, 4]``, whose multiple
    root takes power steps, `CARF` returns an x-value within ``xtol`` of the root."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_power_steps_are_counted():
    """`CARF` is named ``carf``, at version 1, and the logarithms and power of its power steps are flop-counted."""
    # --- act --------------------------
    result = CARF().solve(lambda x: x**9, -1.0, 4.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert (CARF.name, CARF.version) == ("carf", 1)
    assert result.flop_counts.LOG > 0
    assert result.flop_counts.POW > 0


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
