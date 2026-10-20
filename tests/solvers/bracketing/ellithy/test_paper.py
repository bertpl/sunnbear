"""These tests assert that `Ellithy`, with the stopping criterion of its article's pseudocode, reproduces the iteration
counts of Tables 2 to 5 and 12 of the article, and the statistics of the iteration counts in its Table 7."""

import math
import statistics

import pytest

from sunnbear.solvers import Ellithy, EllithyVariant, Interval, SolveStatus
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import (
    PROBLEMS_BY_NUMBER,
    TABLE_7_BY_VARIANT,
    TABLE_12_BY_VARIANT,
    TABLE_12_FIXED_DELTA_PROBLEM_NAMES,
    TABLES_2_TO_5_BY_VARIANT,
)

# The article's tolerance on |f(x)|, with which its experiments ran.
_ARTICLE_TOL = 1e-14

# The article's runs repeat each problem 10000 times, 480000 runs in total (section 6.4).
_N_RUNS_PER_PROBLEM = 10000


# ==================================================================================================
#  Table 12
# ==================================================================================================
@pytest.mark.parametrize("variant", EllithyVariant)
def test_the_rows_of_table_12_name_every_problem_in_order(variant: EllithyVariant):
    """For each variant, `TABLE_12_BY_VARIANT` holds the 48 problems of `PROBLEMS_BY_NUMBER`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_12_BY_VARIANT[variant]] == [
        problem.name for problem in PROBLEMS_BY_NUMBER.values()
    ]


@pytest.mark.parametrize(
    "variant, problem",
    [
        pytest.param(variant, problem, id=f"{variant}-{problem}")
        for variant, problems in TABLE_12_BY_VARIANT.items()
        for problem in problems
    ],
)
def test_the_iteration_counts_of_table_12_are_reproduced(variant: EllithyVariant, problem: PaperProblem):
    """On every row of Table 12, each variant takes the table's iteration count for its method.

    The solve stops by the article's stopping criterion, with the article's adaptive ``delta``, or with a fixed
    ``delta = 1e-4`` on the problems of `TABLE_12_FIXED_DELTA_PROBLEM_NAMES`.
    """
    # --- arrange ----------------------
    if problem.name in TABLE_12_FIXED_DELTA_PROBLEM_NAMES.get(variant, frozenset()):
        solver = _EllithyWithFixedDelta(variant=variant)
    else:
        solver = _EllithyWithPaperStoppingCriterion(variant=variant)

    # --- act / assert -----------------
    assert _n_iterations_until_stop(solver, problem) == problem.n_iterations


@pytest.mark.parametrize(
    "variant, problem",
    [
        pytest.param(variant, problem, id=f"{variant}-{problem}")
        for variant, problems in TABLE_12_BY_VARIANT.items()
        for problem in problems
        if problem.name in TABLE_12_FIXED_DELTA_PROBLEM_NAMES.get(variant, frozenset())
    ],
)
def test_the_adaptive_delta_takes_1_iteration_fewer_than_table_12_on_the_fixed_delta_problems(
    variant: EllithyVariant, problem: PaperProblem
):
    """On each problem of `TABLE_12_FIXED_DELTA_PROBLEM_NAMES`, the adaptive ``delta`` takes 1 iteration fewer than
    Table 12."""
    # --- act / assert -----------------
    n_iterations = _n_iterations_until_stop(_EllithyWithPaperStoppingCriterion(variant=variant), problem)
    assert n_iterations == problem.n_iterations - 1


# ==================================================================================================
#  Tables 2 to 5 and 7
# ==================================================================================================
@pytest.mark.parametrize(
    "variant, problem",
    [
        pytest.param(variant, problem, id=f"{variant}-{problem}")
        for variant, problems in TABLES_2_TO_5_BY_VARIANT.items()
        for problem in problems
    ],
)
def test_the_iteration_counts_of_tables_2_to_5_are_reproduced(variant: EllithyVariant, problem: PaperProblem):
    """On the problem of each of Tables 2 to 5, each variant takes the table's iteration count for its method.

    The solve stops by the article's stopping criterion, with the article's adaptive ``delta``.
    """
    # --- act / assert -----------------
    n_iterations = _n_iterations_until_stop(_EllithyWithPaperStoppingCriterion(variant=variant), problem)
    assert n_iterations == problem.n_iterations


@pytest.mark.parametrize("variant", EllithyVariant)
def test_the_statistics_of_table_7_are_reproduced(variant: EllithyVariant):
    """The iteration counts of each variant on the 48 problems have the statistics that Table 7 reports for its method.

    The solves stop by the article's stopping criterion, with the article's adaptive ``delta``. Table 7's standard
    deviation is the sample standard deviation over the article's 480000 runs, which repeat each problem 10000 times, so
    it exceeds the standard deviation of the 48 counts by the factor ``sqrt(N / (N - 1))``, with ``N = 480000``.
    """
    # --- act --------------------------
    counts = [
        _n_iterations_until_stop(_EllithyWithPaperStoppingCriterion(variant=variant), problem)
        for problem in PROBLEMS_BY_NUMBER.values()
    ]

    # --- assert -----------------------
    n_runs = _N_RUNS_PER_PROBLEM * len(counts)
    published = TABLE_7_BY_VARIANT[variant]
    assert statistics.mean(counts) == pytest.approx(published["mean"], abs=5e-10)
    assert (min(counts), max(counts), statistics.median(counts)) == (
        published["min"],
        published["max"],
        published["median"],
    )
    std_dev = statistics.pstdev(counts) * math.sqrt(n_runs / (n_runs - 1))
    assert std_dev == pytest.approx(published["std_dev"], abs=5e-10)


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _EllithyWithPaperStoppingCriterion(Ellithy):
    """`_EllithyWithPaperStoppingCriterion` is `Ellithy` with the stopping criterion of the article's pseudocode: the
    solve ends once ``|f(x)| <= 1e-14`` at an x-value that the article tests, and returns that x-value.

    It records in `n_iterations` the number of the iteration in which the solve ends. The tests pass ``xtol = 0``,
    which this class ignores.
    """

    def __init__(self, *, variant: EllithyVariant) -> None:
        """Configure the variant, and start the iteration count at 1.

        The article's pseudocode counts a root at an interval bound as 1 iteration (lines 5 to 10 of each algorithm).
        The framework ends such a solve before `_solve` runs, so `n_iterations` then keeps its initial value.
        """
        super().__init__(variant=variant)
        self.n_iterations = 1

    def _root_if_converged(
        self,
        interval: Interval,
        xtol_doubled: float,
        n: int,
        tested_evaluations: tuple[tuple[float, float], ...],
    ) -> float | None:
        """Return the first x-value of ``tested_evaluations`` with ``|f(x)| <= 1e-14``, and record ``n``, or return
        ``None`` if the solve continues; ``interval`` and ``xtol_doubled`` are ignored."""
        for x, fx in tested_evaluations:
            if abs(fx) <= _ARTICLE_TOL:
                self.n_iterations = n
                return x
        return None


class _EllithyWithFixedDelta(_EllithyWithPaperStoppingCriterion):
    """`_EllithyWithFixedDelta` is `_EllithyWithPaperStoppingCriterion` with a fixed step ``delta = 1e-4`` in the
    modified-secant step: ``0.0*max(1, |x_FP|) + 1e-4`` is exactly 1e-4."""

    _DELTA_FACTOR = 0.0
    _DELTA_OFFSET = 1e-4


def _n_iterations_until_stop(solver: _EllithyWithPaperStoppingCriterion, problem: PaperProblem) -> int:
    """Return the number of iterations that ``solver`` takes on ``problem`` until the article's stopping criterion
    stops it, counted as the article counts them."""
    result = solver.solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300)
    assert result.status is SolveStatus.CONVERGED
    return solver.n_iterations
