"""Pins the `Solver.solve` template method with minimal test-local solvers, one per behavior."""

import math

import pytest

from sunnbear.solvers import Solver, SolveRun, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _RecordingSolver(Solver):
    """Does nothing but keep the run it was handed, so tests can inspect what the template prepared."""

    name = "recording"
    version = 1

    def __init__(self) -> None:
        self.runs: list[SolveRun] = []

    def _solve(self, run: SolveRun) -> float:
        self.runs.append(run)
        return run.x_best


class _MidpointRepeater(Solver):
    """Evaluates the midpoint over and over; the only way out is an interrupt."""

    name = "midpoint_repeater"
    version = 1

    def _solve(self, run: SolveRun) -> float:
        x = 0.5 * (run.a + run.b)
        while True:
            run.f(x)
            run.mark_iteration()


class _RunawaySolver(Solver):
    """Asks for an evaluation far outside the bracket."""

    name = "runaway"
    version = 1

    def _solve(self, run: SolveRun) -> float:
        return run.f(run.b + 1e6 * (run.b - run.a))


class _BuggySolver(Solver):
    """Raises an ordinary exception, as a solver with a bug would."""

    name = "buggy"
    version = 1

    def _solve(self, run: SolveRun) -> float:
        raise RuntimeError("bug")


class _IterationCounter(Solver):
    """Marks a fixed number of iterations and returns."""

    name = "iteration_counter"
    version = 1

    def __init__(self, n: int) -> None:
        self.n = n

    def _solve(self, run: SolveRun) -> float:
        for _ in range(self.n):
            run.mark_iteration()
        return run.x_best


def _increasing(x: float) -> float:
    return x - 0.25


def _decreasing(x: float) -> float:
    return 0.25 - x


# ==================================================================================================
#  Caller errors
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, 0.0), (0.0, 0.0)])
def test_rejects_ill_ordered_bracket(a, b):
    with pytest.raises(ValueError, match="a < b"):
        _RecordingSolver().solve(_increasing, a, b, xtol=1e-3, max_fevals=10)


@pytest.mark.parametrize("f", [lambda x: x + 1.0, lambda x: -x - 1.0])  # both positive, both negative
def test_rejects_same_sign_endpoints(f):
    with pytest.raises(ValueError, match="differ in sign"):
        _RecordingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)


# ==================================================================================================
#  Endpoint evaluations
# ==================================================================================================
def test_endpoints_are_evaluated_and_counted_before_the_algorithm_runs():
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.n_fevals == 2
    assert result.status is SolveStatus.CONVERGED
    assert result.n_iters is None  # the solver never marked an iteration
    assert result.x == 0.5  # x_best starts at the bracket midpoint
    assert solver.runs[0].f.n_fevals == 2


@pytest.mark.parametrize("a, b, root", [(0.25, 1.0, 0.25), (-1.0, 0.25, 0.25)])  # root at the lower / upper end
def test_exact_zero_endpoint_converges_without_running_the_algorithm(a, b, root):
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(_increasing, a, b, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals, result.n_iters) == (root, SolveStatus.CONVERGED, 2, None)
    assert solver.runs == []


@pytest.mark.parametrize("f", [_increasing, _decreasing])
def test_run_is_sign_normalized(f):
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    solver.solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10, record_history=True)

    # --- assert -----------------------
    run = solver.runs[0]
    assert run.fa < 0.0 < run.fb
    assert (run.fa, run.fb) == (-0.25, 0.75)
    assert run.f.history == [(0.0, -0.25), (1.0, 0.75)]  # history sees the normalized function too


# ==================================================================================================
#  Status mapping
# ==================================================================================================
def test_budget_exhaustion_maps_to_max_fevals():
    # --- act --------------------------
    result = _MidpointRepeater().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=7)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 7
    assert result.n_iters == 5  # 7 evaluations: 2 endpoints, then 5 completed midpoint iterations
    assert result.x == 0.5  # best-so-far: the untouched bracket's midpoint


def test_leaving_the_guard_interval_maps_to_diverged():
    # --- act --------------------------
    result = _RunawaySolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.DIVERGED
    assert result.n_fevals == 2


def test_non_finite_value_maps_to_function_error():
    # --- arrange ----------------------
    def f(x: float) -> float:
        return math.nan if x == 0.5 else _increasing(x)

    # --- act --------------------------
    result = _MidpointRepeater().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.FUNCTION_ERROR
    assert result.n_fevals == 3  # the failing evaluation counts


def test_solver_exception_maps_to_solver_error():
    # --- act --------------------------
    result = _BuggySolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.SOLVER_ERROR
    assert result.x == 0.5


# ==================================================================================================
#  Result fields
# ==================================================================================================
@pytest.mark.parametrize("n", [1, 3])
def test_marked_iterations_are_reported(n):
    # --- act --------------------------
    result = _IterationCounter(n).solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.n_iters == n


def test_history_is_none_unless_requested():
    # --- act --------------------------
    off = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)
    on = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10, record_history=True)

    # --- assert -----------------------
    assert off.history is None
    assert on.history == ((0.0, -0.25), (1.0, 0.75))


def test_solver_arithmetic_is_counted_and_result_x_is_a_plain_float():
    # --- act --------------------------
    result = _MidpointRepeater().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=3)

    # --- assert -----------------------
    assert result.flop_counts.total_count() > 0  # 0.5 * (a + b) on CountedFloat endpoints
    assert type(result.x) is float
