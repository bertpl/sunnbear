"""These tests assert that `ModAB` reproduces Tables 1 and 2 of its paper."""

import pytest

from sunnbear.solvers import ModAB, SolveStatus
from tests.solvers.bracketing.modab.paper_problems import PAPER_PROBLEMS, PaperProblem

# On these problems, the evaluation count differs from Table 2's, presumably because the authors' .NET runtime rounds
# the last bit of cos, cbrt or exp differently from the correctly rounded values of `PAPER_PROBLEMS`, which changes
# the x-values that the solve evaluates.
_ROUNDING_SENSITIVE_PROBLEM_NAMES = {"f34", "f70", "f86"}


@pytest.mark.parametrize("paper_problem", PAPER_PROBLEMS, ids=lambda p: p.name)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(paper_problem: PaperProblem):
    """With the paper's tolerances, `ModAB` returns modAB's root in the paper's supplementary results within a
    relative 1e-13, and evaluates as often as Table 2 reports less the clamped iterations: exactly, or within 4 on the
    problems in `_ROUNDING_SENSITIVE_PROBLEM_NAMES`."""
    # --- arrange ----------------------
    if paper_problem.name in _ROUNDING_SENSITIVE_PROBLEM_NAMES:
        max_count_difference = 4
    else:
        max_count_difference = 0

    # --- act --------------------------
    result = _ModABWithPaperTolerances().solve(
        paper_problem.f, paper_problem.a, paper_problem.b, xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.n_fevals - (paper_problem.reported_n_fevals - paper_problem.n_clamped)) <= max_count_difference
    assert result.x == pytest.approx(paper_problem.reported_root, rel=1e-13, abs=0.0)


def test_the_switches_of_table_1_of_the_paper_are_reproduced():
    """On ``x^3 - 0.001`` over ``[-10, 10]``, `ModAB` switches modes in the iterations that the paper's Table 1
    reports:

    - iteration 1: to Anderson-Björck mode;
    - iteration 7: back to bisection;
    - iteration 15: to Anderson-Björck mode again;
    - iteration 24: the solve stops, before evaluating.

    Each switch takes effect from the next iteration, so iterations 1 and 8 to 15 bisect, and the solve evaluates in
    iterations 1 to 23, after its 2 evaluations of the interval's bounds.
    """
    # --- act --------------------------
    result = _ModABWithPaperTolerances().solve(
        lambda x: x * x * x - 0.001, -10.0, 10.0, xtol=0.0, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert _bisection_iterations(result.history) == [1, 8, 9, 10, 11, 12, 13, 14, 15]
    assert result.n_fevals == 2 + 23


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _ModABWithPaperTolerances(ModAB):
    """`_ModABWithPaperTolerances` is `ModAB` with the absolute and relative tolerances of the paper's benchmark."""

    @staticmethod
    def _get_stop_width(xtol: float, x3: float) -> float:
        """Return ``aTol + rTol * |x3|``, ignoring ``xtol``."""
        return 1e-14 + 1e-14 * abs(x3)


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
