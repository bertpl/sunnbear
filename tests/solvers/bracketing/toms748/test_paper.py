"""These tests assert that `TOMS748` reproduces the roots that the authors' code computes, and the evaluation totals
of Table II of its paper."""

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.bracketing.toms748.paper_problems import PAPER_PROBLEMS, PaperProblem


@pytest.mark.parametrize("problem", PAPER_PROBLEMS, ids=str)
def test_k_2_reproduces_the_root_that_the_authors_code_computes(problem: PaperProblem):
    """With ``k = 2`` and ``tol = 0``, the setting of the authors' test runs, `TOMS748` returns the root that the
    authors' code prints, within a relative 1e-13, the precision of its 14 printed digits."""
    # --- arrange ----------------------
    a, b = problem.interval

    # --- act --------------------------
    # An xtol of 0 makes tol 0.
    result = TOMS748(k=2).solve(problem.f, a, b, xtol=0.0, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(problem.root, rel=1e-13, abs=0.0)


@pytest.mark.parametrize(
    "k, n_digits, paper_total",
    [
        (1, 7, 2696),
        (1, 10, 2835),
        (1, 15, 2908),
        (1, None, 2950),
        (2, 7, 2650),
        (2, 10, 2786),
        (2, 15, 2859),
        (2, None, 2884),
    ],
)
def test_the_total_evaluation_count_lies_within_1_1_percent_of_the_papers_table_ii(k, n_digits, paper_total):
    """Over the problems in `PAPER_PROBLEMS`, the total evaluation count lies within 1.1 % of the paper's Table II,
    for each ``k`` and for each of the paper's tolerances ``tol = 10^-n_digits`` and ``tol = 0``.

    The paper's counts include the 2 evaluations at the interval bounds, and come from a machine whose relative
    precision was 1.907e-16, not 2^-52.
    """
    # --- arrange / act ----------------
    total = sum(
        _TOMS748WithTol(k=k, n_digits=n_digits).solve(problem.f, *problem.interval, xtol=0.0, max_fevals=100).n_fevals
        for problem in PAPER_PROBLEMS
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.011 * paper_total


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _TOMS748WithTol(TOMS748):
    """`_TOMS748WithTol` is `TOMS748` with the paper's ``tol`` given directly, as the authors' driver gives it."""

    def __init__(self, *, k: int, n_digits: int | None) -> None:
        """Configure ``k`` and the fixed ``tol = 10^-n_digits``, or ``tol = 0`` for ``None``."""
        super().__init__(k=k)
        self._tol = self._tol_as_the_driver_computes_it(n_digits)

    def _get_tol(self, xtol: float, a0: float, b0: float) -> float:
        """Return the fixed ``tol``."""
        return self._tol

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _tol_as_the_driver_computes_it(n_digits: int | None) -> float:
        """Return ``10^-n_digits`` by repeated division, as the subroutine ``TOLE`` of the authors' code computes it,
        or 0 for ``None``."""
        if n_digits is None:
            return 0.0
        else:
            tol = 1.0
            for _ in range(n_digits):
                tol = tol / 10.0
            return tol
