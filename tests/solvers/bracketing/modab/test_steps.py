"""These tests assert that the individual steps of `ModAB` and `ModABSafeguarded` follow their algorithms, and that both
stop by the shared stopping criterion."""

import pytest

from sunnbear.solvers import ModAB, ModABSafeguarded, SolveStatus
from tests.solvers.example_functions import cubic
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem

from .history_replay import bisection_iterations
from .paper_problems import EQUATION_27


@pytest.mark.parametrize("solver_cls", [ModAB, ModABSafeguarded], ids=lambda cls: cls.__name__)
def test_the_first_step_is_a_bisection(solver_cls):
    """Both classes start in bisection mode, so their first x-value is the midpoint of the interval."""
    # --- act --------------------------
    result = solver_cls().solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 1.5


@pytest.mark.parametrize("solver_cls", [ModAB, ModABSafeguarded], ids=lambda cls: cls.__name__)
def test_a_straight_line_switches_to_anderson_bjorck_whose_first_step_lands_on_the_root(solver_cls):
    """On a line, the midpoint lies exactly on the secant, so the method switches to Anderson-Björck mode, and the
    secant's zero is the root, where the function is exactly 0: 4 evaluations in total."""
    # --- act --------------------------
    result = solver_cls().solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values == (0.0, 1.0, 0.5, 0.25)
    assert (result.x, result.status) == (0.25, SolveStatus.CONVERGED)


@pytest.mark.parametrize("solver_cls", [ModAB, ModABSafeguarded], ids=lambda cls: cls.__name__)
def test_the_solve_returns_the_midpoint_of_an_interval_at_most_2_xtol_wide(solver_cls):
    """Both classes stop once the interval is at most ``2*xtol`` wide, and return its midpoint; on the increasing
    `cubic`, the final interval's bounds are the evaluated x-values closest to the root on either side."""
    # --- act --------------------------
    result = solver_cls().solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    x1 = max(x for x, fx in result.history if fx < 0.0)
    x2 = min(x for x, fx in result.history if fx > 0.0)
    assert x2 - x1 <= 2e-6
    assert result.x == 0.5 * (x1 + x2)


@pytest.mark.parametrize(
    "solver_cls, x_second_secant",
    [
        (ModAB, -111.0 / 232.0),
        (ModABSafeguarded, pytest.approx(-75.0 / 121.0, rel=1e-15)),
    ],
    ids=["ModAB", "ModABSafeguarded"],
)
def test_only_modab_safeguarded_scales_no_stored_value_in_its_first_anderson_bjorck_step(solver_cls, x_second_secant):
    """On ``-x^2`` below 0 and ``7*x^2`` from 0, over ``[-3, 1]``, the preprint's equation 27, both classes switch at
    the first midpoint, -1, and their first secant's zero is -0.75; the midpoint and the secant's zero each replace
    the lower bound. Their second secant's zero shows whether the first Anderson-Björck step scaled ``y2 = 7``:

    - `ModABSafeguarded` starts the phase with no bound recorded, so it does not scale ``y2``, and its second secant's
      zero is ``-75/121``, which the preprint's Proposition 3.6 gives;
    - `ModAB` recorded the upper bound as retained in the bisection step that switched, so it multiplies ``y2`` by
      ``m = 1 - 0.5625``, which puts its second secant's zero at ``-111/232``.
    """
    # --- act --------------------------
    result = solver_cls().solve(
        EQUATION_27.f, EQUATION_27.a, EQUATION_27.b, xtol=1e-10, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values[2:5] == (-1.0, -0.75, x_second_secant)


@pytest.mark.parametrize(
    "problem, expected_bisection_iterations",
    [(GanchovskiEtAlTable2Problem.F92.value, [1, 5]), (EQUATION_27, [1, 8])],
    ids=str,
)
def test_modab_safeguarded_falls_back_once_a_step_leaves_the_interval_too_wide_without_an_exception(
    problem: PaperProblem, expected_bisection_iterations: list[int]
):
    """`ModABSafeguarded` switches to Anderson-Björck mode in iteration 1, and falls back to bisection after the first
    Anderson-Björck step that leaves the interval wider than the threshold without being granted a residual exception:

    - on f92, ``x^3 - 0.001`` over ``[-10, 10]``, Anderson-Björck step 3 is the first to leave the interval too wide,
      and ``|y3|`` is far above half the smaller ``|y|`` at the bounds, so the solve falls back at once, and iteration
      5 bisects;
    - on the preprint's equation 27 over ``[-3, 1]``, the interval stays about 1 wide, too wide from Anderson-Björck
      step 3 on, while ``|y3|`` stays below half the smaller ``|y|`` at the bounds. Steps 3 to 5 are each granted an
      exception, step 6 is granted none because at most 3 steps in a row may be granted one, and iteration 8
      bisects, as the preprint's Section 7.4 reports.
    """
    # --- act --------------------------
    result = ModABSafeguarded().solve(problem.f, problem.a, problem.b, xtol=1e-10, max_fevals=100, history_enabled=True)

    # --- assert -----------------------
    assert bisection_iterations(result.history, ModABSafeguarded)[:2] == expected_bisection_iterations


@pytest.mark.parametrize(
    "solver_cls, evaluated_x_values",
    [
        (ModAB, (-1.0, 1.0, 0.0, 0.25)),
        (ModABSafeguarded, (-1.0, 1.0, 0.0, 0.5, 0.25)),
    ],
    ids=["ModAB", "ModABSafeguarded"],
)
def test_modab_safeguarded_skips_the_switching_test_where_y2_minus_y1_overflows(solver_cls, evaluated_x_values):
    """On the line ``1.2e308*(x - 0.25)`` over ``[-1, 1]``, ``y2 - y1`` overflows at the first midpoint, 0:

    - `ModABSafeguarded` skips the switching test there, and bisects once more, to 0.5, where ``y2 - y1`` is finite
      and the line passes the test; its secant's zero is then the root;
    - `ModAB` divides by the infinite ``y2 - y1``, which gives ``r = 1``, so it switches at 0 already.
    """
    # --- act --------------------------
    result = solver_cls().solve(
        lambda x: 1.2e308 * (x - 0.25), -1.0, 1.0, xtol=1e-10, max_fevals=10, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values == evaluated_x_values
    assert result.x == 0.25


def test_the_safeguarded_secant_halves_both_ordinates_where_their_sum_overflows():
    """On `_function_with_huge_values`, the switch happens at the midpoint 0, after which ``|y1| + |y2|`` overflows;
    the secant of `ModABSafeguarded` halves both ordinates, and its zero is the root of the function's linear part left
    of 0, ``-1 + 8/23``."""
    # --- act --------------------------
    result = ModABSafeguarded().solve(
        _function_with_huge_values, -1.0, 1.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values[2:4] == (0.0, pytest.approx(-15.0 / 23.0, rel=1e-15))
    assert result.status is SolveStatus.CONVERGED


@pytest.mark.parametrize(
    "problem, n_x3_on_a_bound",
    [
        (PaperProblem(name="cubic", f=cubic, a=1.0, b=2.0), 1),
        (GanchovskiEtAlTable2Problem.F02.value, 3),
    ],
    ids=str,
)
def test_modab_safeguarded_projects_x3_into_the_interval_and_evaluates_nothing_on_a_bound(
    problem: PaperProblem, n_x3_on_a_bound: int
):
    """At ``xtol = 1e-13``, every ``x3`` of `ModABSafeguarded` lies in its interval, ``n_x3_on_a_bound`` of them on a
    bound, and the solve evaluates no x-value twice: an iteration whose ``x3`` lies on a bound reuses the function
    value there.

    On `cubic`, 1 secant's zero rounds above the interval, and on f02, 1 rounds below it and 2 others land on its lower
    bound; the projection puts each of them on a bound.
    """
    # --- arrange ----------------------
    solver = _ModABSafeguardedRecordingIterations()

    # --- act --------------------------
    result = solver.solve(problem.f, problem.a, problem.b, xtol=1e-13, max_fevals=60)

    # --- assert -----------------------
    assert all(x1 <= x3 <= x2 for x1, x3, x2 in solver.iterations)
    assert sum(x3 in (x1, x2) for x1, x3, x2 in solver.iterations) == n_x3_on_a_bound
    assert len(set(result.evaluated_x_values)) == len(result.evaluated_x_values)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _function_with_huge_values(x: float) -> float:
    """Return the value at ``x`` of a function that reaches 1.5e308 on ``[-1, 1]``, computed without overflow.

    Left of 0, the function is the line ``2.3e308*(x + 1) - 8e307``; it is 1.5e308 at 0 and has its root at
    ``-1 + 8/23``. Right of 0, it falls linearly to 8.0001e307 at 1.
    """
    if x <= 0.0:
        return (1.15e308 * (x + 1.0) - 8e307) + 1.15e308 * (x + 1.0)
    else:
        return 1.5e308 - 6.9999e307 * x


class _ModABSafeguardedRecordingIterations(ModABSafeguarded):
    """`_ModABSafeguardedRecordingIterations` is `ModABSafeguarded` that records ``(x1, x3, x2)`` in ``iterations`` at
    each check of the stopping criterion, which follows the computation of ``x3`` in each iteration."""

    def __init__(self) -> None:
        """Start with no recorded iterations."""
        super().__init__()
        self.iterations: list[tuple[float, float, float]] = []

    def _root_if_converged(
        self, x1: float, y1: float, x2: float, y2: float, x3: float, xtol_doubled: float
    ) -> float | None:
        """Record ``(x1, x3, x2)``, and return what `ModABSafeguarded._root_if_converged` returns."""
        self.iterations.append((float(x1), float(x3), float(x2)))
        return ModABSafeguarded._root_if_converged(x1, y1, x2, y2, x3, xtol_doubled)
