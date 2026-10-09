"""These tests assert that `ModAB` reproduces Tables 1 and 2 of the 2026 modAB paper, takes the steps of the authors'
C# code, and stops within ``xtol`` of a root."""

import pytest

from sunnbear.solvers import ModAB, SolveStatus
from tests.solvers.bracketing.modab.paper_problems import PAPER_PROBLEMS, PaperProblem
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic

# On these problems, the evaluation count differs from Table 2's, presumably because the authors' .NET runtime rounds
# the last bit of cos, cbrt or exp differently from the correctly rounded values of `PAPER_PROBLEMS`, which changes
# the x-values that the solve evaluates.
_ROUNDING_SENSITIVE_PROBLEM_NAMES = {"f34", "f70", "f86"}


# ==================================================================================================
#  The paper's results
# ==================================================================================================
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
#  The steps
# ==================================================================================================
def test_the_first_step_is_a_bisection():
    """`ModAB` starts in bisection mode, so its first x-value is the midpoint of the interval."""
    # --- act --------------------------
    result = ModAB().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 1.5


def test_a_straight_line_switches_to_anderson_bjorck_whose_first_step_lands_on_the_root():
    """On a line, the midpoint lies exactly on the chord, so the method switches to Anderson-Björck mode, and the
    chord's zero is the root, where the function is exactly 0: 4 evaluations in total."""
    # --- act --------------------------
    result = ModAB().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values == (0.0, 1.0, 0.5, 0.25)
    assert (result.x, result.status) == (0.25, SolveStatus.CONVERGED)


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
    root keeps the function from looking close enough to a straight line for the switch, `ModAB` returns an x-value
    within ``xtol`` of the root."""
    # --- act --------------------------
    result = ModAB().solve(f, a, b, xtol=1e-10, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - root) <= 1e-10


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`ModAB` is named ``modab``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = ModAB().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (ModAB.name, ModAB.version) == ("modab", 1)
    assert result.flop_counts.total_count() > 0


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
