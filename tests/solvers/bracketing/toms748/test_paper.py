"""These tests assert that `TOMS748`, with the termination test of the paper's section 6, reproduces the published
results of Alefeld, Potra and Shi (1995):

- the roots of the authors' test output, with ``tol = 0``;
- the totals of the paper's Table II, within a relative tolerance per ``k``;
- the evaluation counts of the paper's Tables IV to VI, with ``tol = 10^-15``.

The tests pass the paper's tolerance ``tol`` as ``xtol``, which `TOMS748` takes as ``tol``.
"""

import pytest

from sunnbear.solvers import TOMS748, SolveState, SolveStatus
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import AlefeldPotraShiTablesIVToVIProblem

from .paper_problems import AUTHORS_TEST_OUTPUT, TABLES_IV_TO_VI_BY_K

# Problem 26[n=1], the paper's problem 13, is 0 on the interval around its root 0 on which exp(1 / x^2) overflows, so
# any x-value of that interval is a root of the function as computed.
_ZERO_ON_AN_INTERVAL_PROBLEM_NAME = "26[n=1]"

# The paper's Table II gives the total evaluation count over all 154 problems, per k and per tol.
_TABLE_II_TOTALS = {
    1: {1e-7: 2696, 1e-10: 2835, 1e-15: 2908, 0.0: 2950},
    2: {1e-7: 2650, 1e-10: 2786, 1e-15: 2859, 0.0: 2884},
}

# Each k has its own relative tolerance on the totals of Table II: the largest deviation of its totals on macOS,
# rounded up to the next 0.1 %, plus 0.1 % for the problems whose count can differ by 1 between math libraries.
_TABLE_II_REL_TOL = {1: 0.012, 2: 0.004}


@pytest.mark.parametrize("k", [1, 2])
@pytest.mark.parametrize(
    "problem",
    [problem for problem in AUTHORS_TEST_OUTPUT if problem.name != _ZERO_ON_AN_INTERVAL_PROBLEM_NAME],
    ids=str,
)
def test_the_roots_of_the_authors_test_output_are_reproduced(problem: PaperProblem, k: int):
    """On each problem of the authors' test output except 26[n=1], both algorithms with ``tol = 0`` return the root
    that the test output prints, within its 14 printed digits."""
    # --- act --------------------------
    result = _TOMS748WithPaperStoppingCriterion(k=k).solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=1000)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("k", [1, 2])
def test_the_solve_of_problem_26_ends_where_its_function_is_0(k: int):
    """On problem 26[n=1], both algorithms with ``tol = 0`` end at an x-value where the function is exactly 0.

    The solve ends at the first x-value that it evaluates where the function is 0, which differs from the x-value of
    the authors' test output.
    """
    # --- arrange ----------------------
    (problem,) = [problem for problem in AUTHORS_TEST_OUTPUT if problem.name == _ZERO_ON_AN_INTERVAL_PROBLEM_NAME]

    # --- act --------------------------
    result = _TOMS748WithPaperStoppingCriterion(k=k).solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=1000)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert problem.f(result.x) == 0.0


@pytest.mark.parametrize(
    "k, tol, paper_total",
    [(k, tol, total) for k, totals in _TABLE_II_TOTALS.items() for tol, total in totals.items()],
)
def test_the_totals_of_table_ii_are_reproduced_within_the_tolerance_of_k(k: int, tol: float, paper_total: int):
    """Over all 154 problems, the total evaluation count of each algorithm, at each of the paper's tolerances, lies
    within the relative tolerance for its ``k`` of the total in the paper's Table II.

    The totals include the 2 evaluations at the interval bounds of each problem, as the counts of Tables IV to VI do.
    """
    # --- arrange ----------------------
    solver = _TOMS748WithPaperStoppingCriterion(k=k)

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
    result = _TOMS748WithPaperStoppingCriterion(k=k).solve(problem.f, problem.a, problem.b, xtol=1e-15, max_fevals=1000)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _TOMS748WithPaperStoppingCriterion(TOMS748):
    """`_TOMS748WithPaperStoppingCriterion` is `TOMS748` with the termination test of the subroutine
    ``bracket`` of the paper's section 6."""

    def _root_if_converged(
        self, state: SolveState, a: float, fa: float, b: float, fb: float, xtol_doubled: float
    ) -> float | None:
        """Return the x-value where ``f`` is 0, or else the midpoint once ``b - a <= 2*tole(a, b)``, or ``None`` if the
        solve continues.

        The paper terminates at ``c`` where ``f(c) = 0``, and ``bracket`` returns that ``c`` as ``a``. The paper
        does not state which x-value its termination test returns once the interval is narrow enough; this method
        returns the midpoint, as the shared stopping criterion does.
        """
        if fa == 0.0:
            return a
        elif fb == 0.0:
            return b
        elif b - a <= 2.0 * self.tole(a, fa, b, fb, state.xtol):
            return 0.5 * (a + b)
        else:
            return None
