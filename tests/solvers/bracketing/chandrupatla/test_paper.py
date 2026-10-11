"""These tests assert that `Chandrupatla` reproduces the evaluation counts and the bisection-switch counts of Table 2
of its paper."""

import pytest

from sunnbear.solvers import Chandrupatla
from tests.solvers.paper_problems import PaperProblem

from .paper_problems import TABLE_2, TABLE_2_N_BISECTION_SWITCHES


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every row of the paper's Table 2, `Chandrupatla` evaluates exactly as often as the paper reports.

    The paper's absolute tolerance is 1e-5, and its relative tolerance of 1e-10 makes no difference to these counts,
    so the solver's ``xtol`` of 1e-5 reproduces them.
    """
    # --- act --------------------------
    result = Chandrupatla().solve(problem.f, problem.a, problem.b, xtol=1e-5, max_fevals=100)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_bisection_switch_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every row of the paper's Table 2, `Chandrupatla` switches to bisection exactly as often as the paper reports.

    The paper counts the iterations that bisect because the paper's condition for using inverse quadratic
    interpolation fails, and leaves out the first iteration, which always bisects.
    """
    # --- act --------------------------
    result = Chandrupatla().solve(problem.f, problem.a, problem.b, xtol=1e-5, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    assert _count_bisection_switches(result.history) == TABLE_2_N_BISECTION_SWITCHES[problem.name]


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _count_bisection_switches(history: list[tuple[float, float]]) -> int:
    """Return the number of iterations, the first one excluded, that evaluate the exact midpoint of the interval.

    ``history`` holds every ``(x, f(x))`` of a `Chandrupatla` solve, in order, starting with the evaluations at ``a``
    and ``b``.

    The function tracks the interval as the paper's listing arranges it: ``x1`` is the newest x-value, and ``x2`` the
    interval bound where ``f`` has the opposite sign of ``f`` at ``x1``. Each iteration evaluates
    ``x1 + t * (x2 - x1)``, so a bisection evaluates ``x1 + 0.5 * (x2 - x1)``.

    A bisection is the only step that evaluates this exact midpoint: the clamp that keeps ``t`` away from 0 and 1
    leaves ``t = 0.5`` unchanged, and an interpolated ``t`` of exactly 0.5 does not occur on the rows of Table 2.
    """
    (x1, f1), (x2, _) = history[0], history[1]
    n_switches = 0
    for i_iteration, (x, f) in enumerate(history[2:]):
        if i_iteration > 0 and x == x1 + 0.5 * (x2 - x1):
            n_switches += 1
        if (f > 0.0) != (f1 > 0.0):
            x2 = x1
        x1, f1 = x, f
    return n_switches
