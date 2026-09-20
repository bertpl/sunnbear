"""Two test-local bracketing solvers pin the loop, the stopping rule, and the state threading of `BracketingSolver`."""

import math

import pytest

from sunnbear.solvers import BracketingSolver, Interval, SolveRun, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _HalvingSolver(BracketingSolver[None]):
    """`_HalvingSolver` splits the bracket at its midpoint and carries no state."""

    name = "halving"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> tuple[Interval, None]:
        x = interval.midpoint
        return interval.replace(x, run.f(x)), None


class _StepCountingSolver(BracketingSolver[int]):
    """`_StepCountingSolver` halves like `_HalvingSolver` but counts its own steps in the threaded state."""

    name = "step_counting"
    version = 1

    def __init__(self) -> None:
        self.states_seen: list[int] = []

    def _initial_state(self, run: SolveRun, interval: Interval) -> int:
        return 0

    def _step(self, run: SolveRun, interval: Interval, state: int) -> tuple[Interval, int]:
        self.states_seen.append(state)
        x = interval.midpoint
        return interval.replace(x, run.f(x)), state + 1


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
    assert result.n_iters == 2  # two completed steps: [0, 0.5], then [0.25, 0.5]
    assert result.x == 0.375


# ==================================================================================================
#  State threading
# ==================================================================================================
def test_state_is_threaded_from_the_initial_state_through_every_step():
    # --- arrange ----------------------
    solver = _StepCountingSolver()

    # --- act --------------------------
    result = solver.solve(_linear, 0.0, 1.0, xtol=1e-3, max_fevals=200)

    # --- assert -----------------------
    assert solver.states_seen == list(range(result.n_iters))
