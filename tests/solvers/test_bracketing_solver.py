"""Two test-local bracketing solvers exercise the loop, stopping rule, and state subclassing of `BracketingSolver`."""

import math
from dataclasses import dataclass

import pytest

from sunnbear.solvers import BracketingSolver, Interval, SolverState, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _HalvingSolver(BracketingSolver):
    """`_HalvingSolver` splits the bracket at its midpoint and adds no state of its own."""

    name = "halving"
    version = 1

    def _step(self, state: SolverState, interval: Interval) -> Interval:
        x = interval.midpoint
        return interval.split_at(x, state.f(x))


@dataclass
class _StepCountingState(SolverState):
    """`_StepCountingState` adds the solver's own step count to the framework's state."""

    n_steps: int = 0


class _StepCountingSolver(BracketingSolver[_StepCountingState]):
    """`_StepCountingSolver` halves like `_HalvingSolver` but counts its own steps in its state subclass."""

    name = "step_counting"
    version = 1
    state_cls = _StepCountingState

    def __init__(self) -> None:
        self.states_seen: list[int] = []

    def _step(self, state: _StepCountingState, interval: Interval) -> Interval:
        self.states_seen.append(state.n_steps)
        state.n_steps += 1
        x = interval.midpoint
        return interval.split_at(x, state.f(x))


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
    n_iters_expected = max(0, math.ceil(math.log2((b - a) / (2.0 * xtol))))
    assert result.status is SolveStatus.CONVERGED
    assert result.n_iters == n_iters_expected
    assert result.n_fevals == n_iters_expected + 2
    assert abs(result.x - 0.3) <= xtol


def test_loop_stops_early_on_an_exact_zero():
    # --- arrange ----------------------
    def f(x: float) -> float:
        return 0.0 if x == 0.5 else _linear(x)  # the first midpoint is an exact root

    # --- act --------------------------
    result = _HalvingSolver().solve(f, 0.0, 1.0, xtol=1e-9, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_iters, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 1, 3)


def test_interrupted_loop_reports_the_last_bracket_midpoint():
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, 0.0, 1.0, xtol=1e-9, max_fevals=4)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_iters == 2  # two steps completed: the bracket became [0, 0.5], then [0.25, 0.5]
    assert result.x == 0.375


# ==================================================================================================
#  State subclassing
# ==================================================================================================
def test_a_solver_gets_a_fresh_instance_of_its_own_state_class_per_solve():
    # --- arrange ----------------------
    solver = _StepCountingSolver()

    # --- act --------------------------
    first = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)
    second = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert solver.states_seen == list(range(first.n_iters)) + list(range(second.n_iters))
