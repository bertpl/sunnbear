"""These tests assert that `Chandrupatla`, with the stopping criterion of its paper's BASIC listing, reproduces the
evaluation counts of Table 2 of its paper, and the number of times that it switches to bisection on each case."""

import pytest

from sunnbear.solvers import Chandrupatla
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import ChandrupatlaTable2Problem

from .paper_problems import TABLE_2, TABLE_2_WITH_N_BISECTION_SWITCHES

# The listing's absolute tolerance is eps_a = 1e-5, and `Chandrupatla` sets eps_a = 2*xtol.
_XTOL = 0.5e-5


def test_the_rows_of_table_2_name_every_problem_of_the_table_in_order():
    """`TABLE_2` holds 1 problem per member of `ChandrupatlaTable2Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_2] == [member.value.name for member in ChandrupatlaTable2Problem]


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """On every row of the paper's Table 2, `Chandrupatla` with the listing's stopping criterion evaluates exactly as
    often as the paper reports.

    The listing's relative tolerance of 1e-10 makes no difference to these counts, so `Chandrupatla`'s relative
    tolerance of 0 reproduces them.
    """
    # --- act --------------------------
    result = _ChandrupatlaWithListingStoppingCriterion().solve(
        problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("problem, n_bisection_switches", TABLE_2_WITH_N_BISECTION_SWITCHES, ids=str)
def test_the_bisection_switch_counts_of_table_2_of_the_paper_are_reproduced(
    problem: PaperProblem, n_bisection_switches: int
):
    """On every row of the paper's Table 2, `Chandrupatla` with the listing's stopping criterion switches to bisection
    exactly as often as the paper reports.

    The paper counts each iteration that bisects because the paper's condition for using inverse quadratic
    interpolation fails. The count leaves out the first iteration, which always bisects.
    """
    # --- act --------------------------
    result = _ChandrupatlaWithListingStoppingCriterion().solve(
        problem.f, problem.a, problem.b, xtol=_XTOL, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert _count_bisection_switches(result.history) == n_bisection_switches


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _ChandrupatlaWithListingStoppingCriterion(Chandrupatla):
    """`_ChandrupatlaWithListingStoppingCriterion` is `Chandrupatla` with the stopping criterion and the return value
    of the paper's BASIC listing ``NEWZERO.BAS``."""

    @staticmethod
    def _root_if_converged(x1: float, f1: float, x2: float, f2: float, xtol_doubled: float) -> float | None:
        """Return ``xm``, the interval bound with the smaller ``|f|``, once ``tl > 0.5`` or ``f(xm) = 0``, or ``None``
        if the solve continues.

        As in the listing, ``tl = tol / |x2 - x1|``, with ``tol = 0.5*eps_a`` and ``eps_a = xtol_doubled``, which
        `Chandrupatla` sets to ``2*xtol``. ``xm`` is the newest x-value ``x1`` when both ``|f|`` are equal.
        """
        xm, fm = x1, f1
        if abs(f2) < abs(f1):
            xm, fm = x2, f2
        tl = 0.5 * xtol_doubled / abs(x2 - x1)
        if tl > 0.5 or fm == 0.0:
            return xm
        else:
            return None


def _count_bisection_switches(history: list[tuple[float, float]]) -> int:
    """Return the number of iterations after the first that evaluate the exact midpoint of the interval.

    ``history`` holds every ``(x, f(x))`` of a `Chandrupatla` solve, in order, starting with the evaluations at ``a``
    and ``b``.

    A bisection is the only step that evaluates this exact midpoint: the clamp that keeps an interpolation step away
    from the interval bounds leaves a bisection unchanged, and an interpolation step to exactly the midpoint does not
    occur on the rows of Table 2.
    """
    # x1 is the newest x-value, and x2 the interval bound where f has the opposite sign of f at x1, as the paper's
    # BASIC listing arranges them.
    (x1, f1), (x2, _) = history[0], history[1]
    n_switches = 0
    for iteration_idx, (x, f) in enumerate(history[2:]):
        # Each iteration evaluates x1 + t * (x2 - x1) for a fraction t between 0 and 1, so a bisection (t = 0.5)
        # evaluates the midpoint.
        if iteration_idx > 0 and x == x1 + 0.5 * (x2 - x1):
            n_switches += 1
        if (f > 0.0) != (f1 > 0.0):
            x2 = x1
        x1, f1 = x, f
    return n_switches
