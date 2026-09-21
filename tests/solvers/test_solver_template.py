"""Each test-local solver here exercises one behavior of the `Solver.solve` template method."""

import math

import pytest

from sunnbear.solvers import Solver, SolverState, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _RecordingSolver(Solver):
    """`_RecordingSolver` keeps the state that it was handed, so tests can inspect what `Solver.solve` prepared."""

    name = "recording"
    version = 1

    def __init__(self) -> None:
        self.states: list[SolverState] = []

    def _solve(self, state: SolverState) -> float:
        self.states.append(state)
        return state.x_best


class _MidpointRepeatingSolver(Solver):
    """`_MidpointRepeatingSolver` evaluates the midpoint over and over, which only an interrupt stops."""

    name = "midpoint_repeater"
    version = 1

    def _solve(self, state: SolverState) -> float:
        x = state.bracket.midpoint
        while True:
            state.f(x)
            state.incr_iteration_count()


class _OutOfBracketSolver(Solver):
    """`_OutOfBracketSolver` asks for an evaluation far outside the bracket."""

    name = "out_of_bracket"
    version = 1

    def _solve(self, state: SolverState) -> float:
        return state.f(state.bracket.b + 1e6 * state.bracket.width)


class _BuggySolver(Solver):
    """`_BuggySolver` raises an ordinary exception, as a solver with a bug would."""

    name = "buggy"
    version = 1

    def _solve(self, state: SolverState) -> float:
        raise RuntimeError("bug")


class _IterationCountingSolver(Solver):
    """`_IterationCountingSolver` marks a fixed number of iterations and returns."""

    name = "iteration_counter"
    version = 1

    def __init__(self, n_iters: int) -> None:
        self.n_iters = n_iters

    def _solve(self, state: SolverState) -> float:
        for _ in range(self.n_iters):
            state.incr_iteration_count()
        return state.x_best


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


@pytest.mark.parametrize(
    "f", [lambda x: x + 1.0, lambda x: -x - 1.0, _decreasing]
)  # the first is positive everywhere, the second negative everywhere, the third has f(a) > 0 > f(b)
def test_rejects_a_function_without_the_required_orientation(f):
    with pytest.raises(ValueError, match=r"f\(a\) < 0 < f\(b\) is required"):
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
    assert result.n_iters is None  # The solver never marked an iteration.
    assert result.x == 0.5  # x_best starts at the bracket midpoint.
    assert solver.states[0].f.n_fevals == 2


@pytest.mark.parametrize(
    "a, b, root", [(0.25, 1.0, 0.25), (-1.0, 0.25, 0.25)]
)  # the root sits at the lower end, then at the upper end
def test_exact_zero_endpoint_converges_without_running_the_algorithm(a, b, root):
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(_increasing, a, b, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals, result.n_iters) == (root, SolveStatus.CONVERGED, 2, None)
    assert solver.states == []


def test_state_holds_the_evaluated_bracket_and_the_history_of_the_evaluations():
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    solver.solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10, record_history=True)

    # --- assert -----------------------
    state = solver.states[0]
    assert (state.bracket.fa, state.bracket.fb) == (-0.25, 0.75)
    assert state.f.history == [(0.0, -0.25), (1.0, 0.75)]


# ==================================================================================================
#  Status mapping
# ==================================================================================================
def test_running_out_of_budget_maps_to_max_fevals():
    # --- act --------------------------
    result = _MidpointRepeatingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=7)

    # --- assert -----------------------
    assert result.status is SolveStatus.MAX_FEVALS
    assert result.n_fevals == 7
    assert result.n_iters == 5  # Of 7 evaluations, 2 went to the endpoints and 5 to completed iterations.
    assert result.x == 0.5  # The best estimate so far is the untouched bracket's midpoint.


def test_leaving_the_guard_interval_maps_to_diverged():
    # --- act --------------------------
    result = _OutOfBracketSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.DIVERGED
    assert result.n_fevals == 2


def test_non_finite_value_maps_to_function_error():
    # --- arrange ----------------------
    def f(x: float) -> float:
        return math.nan if x == 0.5 else _increasing(x)

    # --- act --------------------------
    result = _MidpointRepeatingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.FUNCTION_ERROR
    assert result.n_fevals == 3  # The failing evaluation counts.


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
    result = _IterationCountingSolver(n).solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

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
    result = _MidpointRepeatingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=3)

    # --- assert -----------------------
    assert result.flop_counts.total_count() > 0  # The midpoint arithmetic runs on CountedFloat endpoints.
    assert type(result.x) is float
