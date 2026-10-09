"""These tests assert that `CARF`:

- reproduces Table 4 of its paper;
- still converges on the rows of Table 4 that it does not reproduce;
- comes close to the total evaluation count of Table 3.
"""

import pytest

from sunnbear.solvers import CARF
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import ALEFELD_POTRA_SHI_PROBLEMS

from .paper_problems import TABLE_4


@pytest.mark.parametrize("problem", TABLE_4, ids=str)
def test_the_evaluation_counts_of_table_4_of_the_paper_are_reproduced(problem: PaperProblem):
    """With the paper's tolerances ``eps1 = 1e-15`` and ``eps2 = 1e-12``, `CARF` converges on every row of Table 4,
    and evaluates exactly as often as the table reports on every row that carries no deviation reason."""
    # --- act --------------------------
    result = _CARFWithPaperTolerances(eps1=1e-15, eps2=1e-12).solve(
        problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("eps2, paper_total", [(1e-7, 2456), (1e-10, 2457), (1e-15, 2481)])
def test_the_total_evaluation_count_lies_within_1_5_percent_of_the_papers_table_3(eps2, paper_total):
    """Over the Alefeld-Potra-Shi test problems of Algorithm 748, the total evaluation count lies within 1.5 % of the
    paper's Table 3, at each of that table's tolerances ``eps2``, with ``eps1 = 1e-15`` as in the paper's Table 4."""
    # --- arrange / act ----------------
    total = sum(
        _CARFWithPaperTolerances(eps1=1e-15, eps2=eps2)
        .solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300)
        .n_fevals
        for problem in ALEFELD_POTRA_SHI_PROBLEMS
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
