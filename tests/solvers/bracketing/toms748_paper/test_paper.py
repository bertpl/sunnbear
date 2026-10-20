"""These tests assert that `TOMS748Paper`, with the termination test of the paper's section 6, reproduces the published
results of Alefeld, Potra and Shi (1995):

- the roots of the authors' test output, with ``tol = 0``;
- the totals of the paper's Table II, within a relative tolerance per ``k``;
- the evaluation counts of the paper's Tables IV to VI, with ``tol = 10^-15``.

The tests pass the paper's tolerance ``tol`` as ``xtol``, which `TOMS748Paper` takes as ``tol``.
"""

import pytest

from sunnbear._core.solvers.bracketing.toms748_paper import TOMS748Paper
from sunnbear.solvers import SolveStatus
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import AlefeldPotraShiTablesIVToVIProblem

from .paper_problems import AUTHORS_TEST_OUTPUT, TABLES_IV_TO_VI_BY_K, tol_as_the_driver_computes_it

# Problem 26[n=1], the paper's problem 13, is 0 on the interval around its root 0 where exp(1 / x^2) overflows, so
# any x-value of that interval is a root of the function as computed.
_ZERO_INTERVAL_PROBLEM_NAME = "26[n=1]"

# The paper's Table II: the total evaluation count over all 154 problems, per k and per tol = 10^-n_digits, with
# n_digits = None for tol = 0.
_TABLE_II_TOTALS = {
    1: {7: 2696, 10: 2835, 15: 2908, None: 2950},
    2: {7: 2650, 10: 2786, 15: 2859, None: 2884},
}

# The relative tolerance on the totals of Table II, per k. On macOS, the totals lie 0.24 % to 1.08 % below the paper's
# for k = 1, and 0.10 % to 0.25 % below for k = 2; each tolerance is the next tenth of a percent above the largest of
# these, plus 0.1 %, for the counts of 1 that a platform's math library can shift.
_TABLE_II_REL_TOL = {1: 0.012, 2: 0.004}


@pytest.mark.parametrize("k", [1, 2])
@pytest.mark.parametrize(
    "problem", [problem for problem in AUTHORS_TEST_OUTPUT if problem.name != _ZERO_INTERVAL_PROBLEM_NAME], ids=str
)
def test_the_roots_of_the_authors_test_output_are_reproduced(problem: PaperProblem, k: int):
    """On each problem of the authors' test output except 26[n=1], both algorithms with ``tol = 0`` return the root
    that the test output prints, within its 14 printed digits."""
    # --- act --------------------------
    result = _TOMS748PaperWithPaperTerminationTest(k=k).solve(
        problem.f, problem.a, problem.b, xtol=0.0, max_fevals=1000
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("k", [1, 2])
def test_the_solve_of_problem_26_ends_where_its_function_is_0(k: int):
    """On problem 26[n=1], both algorithms with ``tol = 0`` end at an x-value where the function is exactly 0.

    The function is 0 on the interval around its root 0 where ``exp(1 / x^2)`` overflows, and the solve ends at the
    first x-value of that interval that it evaluates, which differs from the x-value of the authors' test output.
    """
    # --- arrange ----------------------
    (problem,) = [problem for problem in AUTHORS_TEST_OUTPUT if problem.name == _ZERO_INTERVAL_PROBLEM_NAME]

    # --- act --------------------------
    result = _TOMS748PaperWithPaperTerminationTest(k=k).solve(
        problem.f, problem.a, problem.b, xtol=0.0, max_fevals=1000
    )

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert problem.f(result.x) == 0.0


@pytest.mark.parametrize(
    "k, n_digits, paper_total",
    [(k, n_digits, total) for k, totals in _TABLE_II_TOTALS.items() for n_digits, total in totals.items()],
)
def test_the_totals_of_table_ii_are_reproduced_within_the_tolerance_of_k(
    k: int, n_digits: int | None, paper_total: int
):
    """Over all 154 problems, the total evaluation count of each algorithm, at each of the paper's tolerances, lies
    within the relative tolerance of its ``k`` of the paper's Table II.

    The totals count the 2 evaluations at the interval bounds of each problem, the counting with which the counts of
    Tables IV to VI reproduce. They lie below the paper's, for a cause not known, which the docstring of this test
    package discusses.
    """
    # --- arrange ----------------------
    solver = _TOMS748PaperWithPaperTerminationTest(k=k)
    tol = tol_as_the_driver_computes_it(n_digits)

    # --- act --------------------------
    total = sum(
        solver.solve(problem.f, problem.a, problem.b, xtol=tol, max_fevals=1000).n_fevals
        for problem in AUTHORS_TEST_OUTPUT
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= _TABLE_II_REL_TOL[k] * paper_total


@pytest.mark.parametrize("k", [1, 2])
def test_the_rows_of_tables_iv_to_vi_name_every_problem_of_the_tables_in_order(k: int):
    """`TABLES_IV_TO_VI_BY_K` holds, for each ``k``, 1 problem per member of `AlefeldPotraShiTablesIVToVIProblem`, in
    the tables' order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLES_IV_TO_VI_BY_K[k]] == [
        member.value.name for member in AlefeldPotraShiTablesIVToVIProblem
    ]


@pytest.mark.parametrize(
    "k, problem",
    [(k, problem) for k, problems in TABLES_IV_TO_VI_BY_K.items() for problem in problems],
    ids=str,
)
def test_the_evaluation_counts_of_tables_iv_to_vi_are_reproduced(k: int, problem: PaperProblem):
    """On every row of the paper's Tables IV to VI, each algorithm with ``tol = 10^-15`` evaluates as often as the
    paper reports for its ``k``, except where the problem states an allowed deviation."""
    # --- act --------------------------
    result = _TOMS748PaperWithPaperTerminationTest(k=k).solve(
        problem.f, problem.a, problem.b, xtol=tol_as_the_driver_computes_it(15), max_fevals=1000
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _TOMS748PaperWithPaperTerminationTest(TOMS748Paper):
    """`_TOMS748PaperWithPaperTerminationTest` is `TOMS748Paper` with the termination test of the subroutine
    ``bracket`` of the paper's section 6."""

    def _root_if_converged(
        self, a_bar: float, fa_bar: float, b_bar: float, fb_bar: float, tol: float, xtol_doubled: float
    ) -> float | None:
        """Return the x-value where ``f`` is 0, or else the midpoint once ``b_bar - a_bar <= 2*tole(a_bar, b_bar)``, or
        ``None`` if the solve continues.

        The paper terminates at ``c`` where ``f(c) = 0``, and ``bracket`` returns that ``c`` as ``a_bar``. The paper
        does not state which x-value its width test returns; the midpoint is the one of the shared stopping criterion.
        """
        if fa_bar == 0.0:
            return a_bar
        elif fb_bar == 0.0:
            return b_bar
        elif b_bar - a_bar <= 2.0 * self.tole(a_bar, fa_bar, b_bar, fb_bar, tol):
            return 0.5 * (a_bar + b_bar)
        else:
            return None
