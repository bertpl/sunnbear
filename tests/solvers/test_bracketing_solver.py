"""2 test-local bracketing solvers exercise the loop, the stopping rule, the final interval, and state subclasses."""

import math
from dataclasses import dataclass

import pytest

from sunnbear.solvers import (
    BracketingSolver,
    DecreasingInterval,
    IncreasingInterval,
    Interval,
    IntervalBound,
    SolveState,
    SolveStatus,
)


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _HalvingSolver(BracketingSolver):
    """`_HalvingSolver` splits the interval at its midpoint and adds no state of its own."""

    name = "halving"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        return interval.midpoint


@dataclass
class _StepCountingState(SolveState):
    """`_StepCountingState` adds the solver's own step count to the framework's state."""

    n_steps: int = 0


class _StepCountingSolver(BracketingSolver[_StepCountingState]):
    """`_StepCountingSolver` halves like `_HalvingSolver` but counts its own steps in its state subclass."""

    name = "step_counting"
    version = 1
    state_cls = _StepCountingState

    def __init__(self) -> None:
        self.n_steps_seen: list[int] = []

    def _next_x(self, state: _StepCountingState, interval: Interval) -> float:
        self.n_steps_seen.append(state.n_steps)
        state.n_steps += 1
        return interval.midpoint


def _linear(x: float) -> float:
    return x - 0.3


# ==================================================================================================
#  Loop and stopping rule
# ==================================================================================================
@pytest.mark.parametrize("a, b, xtol", [(0.0, 1.0, 1e-3), (-2.0, 3.0, 1e-6), (0.25, 0.5, 0.1)])
def test_loop_runs_until_the_width_criterion_holds(a, b, xtol):
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    n_steps_expected = max(0, math.ceil(math.log2((b - a) / (2.0 * xtol))))
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals == n_steps_expected + 2  # One evaluation per step, plus the 2 interval bounds.
    assert abs(result.x - 0.3) <= xtol


def test_loop_stops_early_on_an_exact_zero():
    # --- arrange ----------------------
    def f(x: float) -> float:
        return 0.0 if x == 0.5 else _linear(x)  # the first midpoint is an exact root

    # --- act --------------------------
    result = _HalvingSolver().solve(f, 0.0, 1.0, xtol=1e-9, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


def test_interrupted_loop_reports_the_last_evaluated_point():
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, 0.0, 1.0, xtol=1e-9, max_fevals=4)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 4  # After the interval bounds, 2 steps evaluated 0.5, then 0.25.
    assert result.x == 0.25


# ==================================================================================================
#  Final interval
# ==================================================================================================
@pytest.mark.parametrize(
    "f, cls_expected", [(_linear, IncreasingInterval), (lambda x: -_linear(x), DecreasingInterval)]
)  # Both orientations are reported with their own class.
def test_the_final_interval_holds_the_root_within_2_xtol_as_plain_floats(f, cls_expected):
    """A converged solve reports its last interval: no wider than `2·xtol`, around the root and the result."""
    # --- act --------------------------
    result = _HalvingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    interval = result.final_interval
    assert type(interval) is cls_expected
    assert interval.a <= 0.3 <= interval.b
    assert interval.b - interval.a <= 2e-3
    assert result.x == 0.5 * (interval.a + interval.b)
    assert all(type(value) is float for value in (interval.a, interval.b, interval.fa, interval.fb))


def test_an_interrupted_solve_reports_its_last_interval():
    """A solve that runs out of budget still reports the interval that its last split produced."""
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, 0.0, 1.0, xtol=1e-9, max_fevals=4)

    # --- assert -----------------------
    # The splits at 0.5, then at 0.25, leave [0.25, 0.5]; the second split replaced the lower bound.
    interval = result.final_interval
    assert result.status is SolveStatus.MAX_FEVALS
    assert (interval.a, interval.b, interval.last_replaced_bound) == (0.25, 0.5, IntervalBound.LOWER)


def test_a_solve_that_ends_at_an_interval_bound_reports_no_final_interval():
    """An exact zero at an interval bound ends the solve before the algorithm runs, so no interval is reported."""
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, 0.3, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert (result.status, result.final_interval) == (SolveStatus.CONVERGED, None)


# ==================================================================================================
#  Subclassing state
# ==================================================================================================
def test_a_solver_gets_a_fresh_instance_of_its_own_state_class_per_solve():
    # --- arrange ----------------------
    solver = _StepCountingSolver()

    # --- act --------------------------
    first = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)
    second = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    n_steps = first.n_fevals - 2  # One evaluation per step; both solves are identical.
    assert second.n_fevals == first.n_fevals
    assert solver.n_steps_seen == list(range(n_steps)) * 2
