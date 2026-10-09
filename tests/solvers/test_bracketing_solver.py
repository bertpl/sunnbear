"""2 test-local bracketing solvers exercise the loop, the stopping rule, and subclassing `SolveState`."""

import math
from dataclasses import dataclass

import pytest

from sunnbear.solvers import BracketingSolver, Interval, SolveState, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _HalvingSolver(BracketingSolver):
    """`_HalvingSolver` splits the interval at its midpoint and adds no state of its own."""

    name = "halving"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the interval midpoint."""
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
        """Start an empty list that collects, across all solves, the step count that `_next_x` reads from the state."""
        self.n_steps_seen: list[int] = []

    def _next_x(self, state: _StepCountingState, interval: Interval) -> float:
        """Append the state's step count to `n_steps_seen`, add 1 to the state's step count, and return the interval
        midpoint."""
        self.n_steps_seen.append(state.n_steps)
        state.n_steps += 1
        return interval.midpoint


def _linear(x: float) -> float:
    """Return the value of a linear function with its root at 0.3."""
    return x - 0.3


# ==================================================================================================
#  Loop and stopping rule
# ==================================================================================================
@pytest.mark.parametrize("a, b, xtol", [(0.0, 1.0, 1e-3), (-2.0, 3.0, 1e-6), (0.25, 0.5, 0.1)])
def test_loop_runs_until_the_width_criterion_holds(a, b, xtol):
    """The loop halves the interval until its width is at most ``2 * xtol``, so the solve converges within ``xtol``
    after 1 evaluation per halving plus the 2 at the interval bounds."""
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    n_steps_expected = max(0, math.ceil(math.log2((b - a) / (2.0 * xtol))))
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals == n_steps_expected + 2  # One evaluation per step, plus the 2 interval bounds.
    assert abs(result.x - 0.3) <= xtol


def test_loop_stops_early_on_an_exact_zero():
    """When the function is exactly zero at the first midpoint, the loop converges there after 3 evaluations."""

    # --- arrange ----------------------
    def f(x: float) -> float:
        """Return the value of `_linear`, except for an exact zero at 0.5."""
        if x == 0.5:
            return 0.0  # the first midpoint is an exact root
        else:
            return _linear(x)

    # --- act --------------------------
    result = _HalvingSolver().solve(f, 0.0, 1.0, xtol=1e-9, max_fevals=200)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.5, SolveStatus.CONVERGED, 3)


def test_interrupted_loop_reports_the_last_evaluated_point():
    """When its budget runs out, the solve reports ``MAX_FEVALS`` with the last evaluated x-value."""
    # --- act --------------------------
    result = _HalvingSolver().solve(_linear, 0.0, 1.0, xtol=1e-9, max_fevals=4)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 4  # After the interval bounds, 2 steps evaluated 0.5, then 0.25.
    assert result.x == 0.25


# ==================================================================================================
#  Subclassing state
# ==================================================================================================
def test_a_solver_gets_a_fresh_instance_of_its_own_state_class_per_solve():
    """Each solve passes a new `_StepCountingState` to `_next_x`, so the step count restarts at 0 for the second
    solve."""
    # --- arrange ----------------------
    solver = _StepCountingSolver()

    # --- act --------------------------
    first = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)
    second = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    n_steps = first.n_fevals - 2  # One evaluation per step; both solves are identical.
    assert second.n_fevals == first.n_fevals
    assert solver.n_steps_seen == list(range(n_steps)) * 2
