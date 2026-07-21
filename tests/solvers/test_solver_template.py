import math

import pytest

from sunnbear.errors import MaxFevalsExceeded
from sunnbear.solvers import Bisection, BracketingSolver, Interval, Solver, SolveRun, SolveStatus, StepOutcome


class _CrashingSolver(Solver):
    name = "crashing"
    version = 1

    def _solve(self, run: SolveRun) -> float:
        raise RuntimeError("bug in solver code")


class _DivergingSolver(Solver):
    name = "diverging"
    version = 1

    def _solve(self, run: SolveRun) -> float:
        x = float(run.b)
        while True:
            x = x * 2.0 + 1.0
            run.f(x)


def test_solver_bug_becomes_solver_error_status():
    # --- act --------------------------
    result = _CrashingSolver().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.SOLVER_ERROR
    assert result.x == pytest.approx(0.5)  # best-so-far fallback: bracket midpoint
    assert result.n_fevals == 2


def test_divergence_becomes_diverged_status():
    # --- act --------------------------
    result = _DivergingSolver().solve(lambda x: x - 0.5, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.DIVERGED


def test_max_fevals_becomes_status_with_best_so_far():
    # --- act --------------------------
    result = Bisection().solve(lambda x: x - 0.3, 0.0, 1.0, xtol=1e-15, max_fevals=6)

    # --- assert -----------------------
    assert result.status == SolveStatus.MAX_FEVALS
    assert result.n_fevals == 6
    assert 0.0 < result.x < 1.0  # best-so-far midpoint, not garbage


def test_function_error_becomes_status():
    # --- arrange ----------------------
    def nan_in_middle(x: float) -> float:
        return math.nan if 0.4 < x < 0.6 else x - 0.3

    # --- act --------------------------
    result = Bisection().solve(nan_in_middle, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.FUNCTION_ERROR


def test_function_error_during_initial_bracket_evaluation():
    # --- act --------------------------
    result = Bisection().solve(lambda x: math.nan, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.FUNCTION_ERROR
    assert result.x == pytest.approx(0.5)  # fallback: bracket midpoint (no run state yet)
    assert result.n_iters is None


def test_base_loop_returns_endpoint_on_exact_zero_fb():
    """A custom _step may hand back an interval whose upper endpoint is an exact zero."""

    # --- arrange ----------------------
    class ZeroFbSolver(BracketingSolver[None]):
        name = "zero_fb"
        version = 1

        def _step(self, run, interval, state):
            return StepOutcome(interval=Interval(interval.a, 0.7, interval.fa, 0.0), state=None)

    # --- act --------------------------
    result = ZeroFbSolver().solve(lambda x: x - 0.7, 0.0, 1.0, xtol=1e-9, max_fevals=100)

    # --- assert -----------------------
    assert result.status == SolveStatus.CONVERGED
    assert result.x == 0.7


def test_interrupt_exceptions_do_not_escape_solve():
    # --- arrange ----------------------
    solver = Bisection()

    # --- act --------------------------
    try:
        result = solver.solve(lambda x: x - 0.3, 0.0, 1.0, xtol=1e-15, max_fevals=4)
    except MaxFevalsExceeded:  # pragma: no cover
        pytest.fail("SolveInterrupt escaped solve()")

    # --- assert -----------------------
    assert result.status == SolveStatus.MAX_FEVALS
