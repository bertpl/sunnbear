"""These tests assert that `ModAB`, with the stopping criterion of its paper's C# code, reproduces Tables 1 and 2 of its
paper."""

import pytest

from sunnbear.solvers import ModAB
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem, ganchovski_et_al_stop_width

from .paper_problems import TABLE_2


def test_the_rows_of_table_2_name_every_problem_of_the_table_in_order():
    """`TABLE_2` holds 1 problem per member of `GanchovskiEtAlTable2Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_2] == [member.value.name for member in GanchovskiEtAlTable2Problem]


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """With the stopping criterion of the paper's C# code and the tolerances of its benchmark, `ModAB` reproduces
    modAB's published results on each problem of Table 2:

    - it returns the root that the paper's supplementary results give, within a relative 1e-13;
    - it evaluates as often as Table 2 reports, less the iterations that the paper's C# code counts but that evaluate
      nothing, except on the few problems whose count depends on how the platform rounds a library function.
    """
    # --- act --------------------------
    result = _ModABWithPaperStoppingCriterion().solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


def test_the_switches_of_table_1_of_the_paper_are_reproduced():
    """On ``x^3 - 0.001`` over ``[-10, 10]``, with the stopping criterion of the paper's C# code and the tolerances of
    its benchmark, `ModAB` switches modes in the iterations that the paper's Table 1 reports:

    - iteration 1: to Anderson-Björck mode;
    - iteration 7: back to bisection;
    - iteration 15: to Anderson-Björck mode again;
    - iteration 24: the solve stops, before evaluating.

    Each switch takes effect from the next iteration, so iterations 1 and 8 to 15 bisect, and the solve evaluates in
    iterations 1 to 23, after its 2 evaluations of the interval's bounds.
    """
    # --- act --------------------------
    result = _ModABWithPaperStoppingCriterion().solve(
        lambda x: x * x * x - 0.001, -10.0, 10.0, xtol=0.0, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert _bisection_iterations(result.history) == [1, 8, 9, 10, 11, 12, 13, 14, 15]
    assert result.n_fevals == 2 + 23


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _ModABWithPaperStoppingCriterion(ModAB):
    """`_ModABWithPaperStoppingCriterion` is `ModAB` with the stopping criterion and the return value of the paper's
    C# code, at the absolute and relative tolerances ``aTol`` and ``rTol`` of the paper's benchmark.

    The tolerances are those of `ganchovski_et_al_stop_width`, so a test passes ``xtol = 0``, which this class ignores.
    """

    @staticmethod
    def _root_if_converged(x1: float, y1: float, x2: float, y2: float, x3: float, xtol_doubled: float) -> float | None:
        """Return ``x3`` once the interval is at most ``aTol + rTol*|x3|`` wide, or ``None`` if the solve continues.

        The C# code tests for a 0 only after evaluating ``x3``, as `ModAB` does, so this check reads no function value.
        """
        if x2 - x1 <= ganchovski_et_al_stop_width(x3):
            return x3
        else:
            return None


def _bisection_iterations(history: tuple[tuple[float, float], ...]) -> list[int]:
    """Return the 1-based numbers of the iterations whose x-value is the midpoint of the interval.

    The interval is replayed from ``history``: each evaluated x-value replaces the bound whose function value has the
    same sign as the function value at that x-value. The replay holds only for a solve without clamped iterations,
    which evaluate nothing.
    """
    (x1, y1), (x2, _) = history[:2]
    iterations = []
    for iteration, (x, y) in enumerate(history[2:], start=1):
        if x == (x1 + x2) / 2.0:
            iterations.append(iteration)
        if (y > 0.0) == (y1 > 0.0):
            x1, y1 = x, y
        else:
            x2 = x
    return iterations
