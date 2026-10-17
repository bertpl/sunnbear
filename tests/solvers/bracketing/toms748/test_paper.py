"""These tests check `TOMS748` against the published results of Algorithm 748, which depend on the stopping criterion
of the authors' code, so they run a subclass of `TOMS748` with that criterion:

- it reproduces the roots that the authors' code computes;
- it reproduces the evaluation counts of the paper's Tables IV to VI;
- its evaluation totals come close to those of the paper's Table II.
"""

import pytest

from sunnbear.solvers import TOMS748, Interval
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import (
    ALEFELD_POTRA_SHI_PROBLEMS,
    AlefeldPotraShiTablesIVToVIProblem,
)

from .paper_problems import AUTHORS_TEST_OUTPUT, PRINTED_ROOTS, TABLES_IV_TO_VI_BY_K


def test_the_printed_roots_name_exactly_the_alefeld_potra_shi_problems():
    """`PRINTED_ROOTS` holds a root for every Alefeld-Potra-Shi problem, and for no other name."""
    # --- assert -----------------------
    assert set(PRINTED_ROOTS) == {problem.name for problem in ALEFELD_POTRA_SHI_PROBLEMS}


@pytest.mark.parametrize("problem", AUTHORS_TEST_OUTPUT, ids=str)
def test_k_2_reproduces_the_root_that_the_authors_code_computes(problem: PaperProblem):
    """With ``k = 2`` and ``tol = 0``, the setting of the authors' test runs, `TOMS748` with the authors' stopping
    criterion converges; wherever the test data holds the root that the authors' code prints, `TOMS748` returns that
    root within a relative 1e-13, the precision of its 14 printed digits."""
    # --- act --------------------------
    result = _TOMS748WithAuthorsStoppingCriterion(k=2).solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("k", [1, 2])
def test_the_rows_of_tables_iv_to_vi_name_every_problem_of_the_tables_in_order(k: int):
    """`TABLES_IV_TO_VI_BY_K` holds, for each ``k``, 1 problem per member of `AlefeldPotraShiTablesIVToVIProblem`, in
    the tables' order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLES_IV_TO_VI_BY_K[k]] == [
        member.value.name for member in AlefeldPotraShiTablesIVToVIProblem
    ]


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
def test_the_total_evaluation_count_lies_within_1_2_percent_of_the_papers_table_ii(k, n_digits, paper_total):
    """Over the problems in `AUTHORS_TEST_OUTPUT`, the total evaluation count of `TOMS748` with the authors' stopping
    criterion lies within 1.2 % of the paper's Table II, for each ``k`` and for each of the paper's tolerances
    ``tol = 10^-n_digits`` and ``tol = 0``.

    The paper's counts include the 2 evaluations at the interval bounds, and come from a machine whose relative
    precision was 1.907e-16, not 2^-52. The totals that this test computes also differ by a few evaluations between
    macOS and Linux, so the tolerance has to cover that difference too.
    """
    # --- arrange / act ----------------
    total = sum(
        _TOMS748WithAuthorsStoppingCriterion(k=k)
        .solve(problem.f, problem.a, problem.b, xtol=_tol_as_the_driver_computes_it(n_digits), max_fevals=100)
        .n_fevals
        for problem in AUTHORS_TEST_OUTPUT
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.012 * paper_total


@pytest.mark.parametrize(
    "k, problem",
    [
        pytest.param(k, problem, id=f"k={k}-{problem.name}")
        for k, problems in TABLES_IV_TO_VI_BY_K.items()
        for problem in problems
    ],
)
def test_the_evaluation_counts_of_tables_iv_to_vi_of_the_paper_are_reproduced(k: int, problem: PaperProblem):
    """On every problem of the paper's Tables IV to VI, `TOMS748` with the authors' stopping criterion and
    ``tol = 10^-15`` evaluates as often as the paper reports for that ``k``, except where the problem states an allowed
    deviation."""
    # --- act --------------------------
    result = _TOMS748WithAuthorsStoppingCriterion(k=k).solve(
        problem.f, problem.a, problem.b, xtol=_tol_as_the_driver_computes_it(15), max_fevals=100
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _TOMS748WithAuthorsStoppingCriterion(TOMS748):
    """`_TOMS748WithAuthorsStoppingCriterion` is `TOMS748` with the stopping criterion of the authors' code, and its
    returned x-value, the lower bound ``a``.

    `TOMS748` takes ``tol = xtol``, so a test passes the paper's ``tol`` as ``xtol``.
    """

    @staticmethod
    def _root_if_converged(interval: Interval, xtol_doubled: float, tole_doubled: float) -> float | None:
        """Return ``a`` if ``f(a) = 0`` or the interval is at most ``2*tole`` wide, else ``None``, ignoring
        ``xtol_doubled``.

        At the top of an iteration, the authors' code checks only the width; ``f(a)`` is never 0 there, because the
        check after the previous evaluation would have ended the solve.
        """
        if interval.is_fa_zero or interval.width <= tole_doubled:
            return interval.a
        else:
            return None


def _tol_as_the_driver_computes_it(n_digits: int | None) -> float:
    """Return ``10^-n_digits`` by repeated division, as the subroutine ``TOLE`` of the authors' code computes it, or 0
    for ``None``."""
    if n_digits is None:
        return 0.0
    else:
        tol = 1.0
        for _ in range(n_digits):
            tol = tol / 10.0
        return tol
