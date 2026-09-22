"""Each test-local solver here exercises one behavior of the `Solver.solve` template method."""

import math

import pytest
from counted_float import FlopCounts

from sunnbear.solvers import DecreasingInterval, IncreasingInterval, Solver, SolveState, SolveStatus


# ==================================================================================================
#  Test-local solvers
# ==================================================================================================
class _RecordingSolver(Solver):
    """`_RecordingSolver` keeps the state that it was handed, so tests can inspect what `Solver.solve` prepared."""

    name = "recording"
    version = 1

    def __init__(self) -> None:
        self.states: list[SolveState] = []

    def _solve(self, state: SolveState) -> float:
        self.states.append(state)
        return state.x_best


class _MidpointRepeatingSolver(Solver):
    """`_MidpointRepeatingSolver` evaluates the midpoint over and over, which only an interrupt stops."""

    name = "midpoint_repeater"
    version = 1

    def _solve(self, state: SolveState) -> float:
        x = state.interval.midpoint
        while True:
            state.f(x)


class _ExcursionSolver(Solver):
    """`_ExcursionSolver` evaluates far outside the interval, then returns an estimate of its choice."""

    name = "excursion"
    version = 1

    def __init__(self, x_returned: float) -> None:
        self._x_returned = x_returned

    def _solve(self, state: SolveState) -> float:
        state.x_best = float(state.interval.b + 1e6 * state.interval.width)
        state.f(state.x_best)
        return self._x_returned


class _NanSolver(Solver):
    """`_NanSolver` asks for an evaluation at NaN, as a runaway whose arithmetic broke down would."""

    name = "nan"
    version = 1

    def _solve(self, state: SolveState) -> float:
        return state.f(math.nan)


class _StrayingSolver(Solver):
    """`_StrayingSolver` moves its best estimate outside the interval and then runs out of budget."""

    name = "straying"
    version = 1

    def _solve(self, state: SolveState) -> float:
        state.x_best = float(state.interval.b + 1.0)
        while True:
            state.f(state.x_best)


class _BuggySolver(Solver):
    """`_BuggySolver` raises an ordinary exception, as a solver with a bug would."""

    name = "buggy"
    version = 1

    def _solve(self, state: SolveState) -> float:
        raise RuntimeError("bug")


def _increasing(x: float) -> float:
    return x - 0.25


def _decreasing(x: float) -> float:
    return 0.25 - x


# ==================================================================================================
#  Caller errors
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, 0.0), (0.0, 0.0)])
def test_rejects_an_ill_ordered_interval(a, b):
    with pytest.raises(ValueError, match="Interval must satisfy a < b"):
        _RecordingSolver().solve(_increasing, a, b, xtol=1e-3, max_fevals=10)


@pytest.mark.parametrize("f", [lambda x: x + 1.0, lambda x: -x - 1.0])  # positive everywhere, negative everywhere
def test_rejects_a_function_without_a_sign_change(f):
    with pytest.raises(ValueError, match="differ in sign"):
        _RecordingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)


@pytest.mark.parametrize(
    "f, cls_expected", [(_increasing, IncreasingInterval), (_decreasing, DecreasingInterval)]
)  # Both orientations are solved; the interval's class tells the solver which one it has.
def test_the_interval_class_is_the_orientation(f, cls_expected):
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert type(solver.states[0].interval) is cls_expected


# ==================================================================================================
#  Evaluations at the interval bounds
# ==================================================================================================
def test_the_interval_bounds_are_evaluated_and_counted_before_the_algorithm_runs():
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.n_fevals == 2
    assert result.status is SolveStatus.CONVERGED
    assert result.x == 0.5  # x_best starts at the interval midpoint.
    assert solver.states[0].f.n_fevals == 2


@pytest.mark.parametrize(
    "a, b, root", [(0.25, 1.0, 0.25), (-1.0, 0.25, 0.25)]
)  # the root sits at the lower end, then at the upper end
def test_an_exact_zero_at_an_interval_bound_converges_without_running_the_algorithm(a, b, root):
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    result = solver.solve(_increasing, a, b, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (root, SolveStatus.CONVERGED, 2)
    assert solver.states == []


def test_state_holds_the_evaluated_interval_and_the_history_of_the_evaluations():
    # --- arrange ----------------------
    solver = _RecordingSolver()

    # --- act --------------------------
    solver.solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    state = solver.states[0]
    assert (state.interval.fa, state.interval.fb) == (-0.25, 0.75)
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
    assert result.x == 0.5  # The best estimate so far is the untouched interval's midpoint.


@pytest.mark.parametrize(
    "x_returned, status_expected",
    [(0.5, SolveStatus.CONVERGED), (1.0, SolveStatus.CONVERGED), (1.0 + 1e-9, SolveStatus.DIVERGED)],
)  # An excursion is not penalized; only the result decides, and an interval bound is inside.
def test_only_a_result_outside_the_interval_is_divergence(x_returned, status_expected):
    # --- act --------------------------
    result = _ExcursionSolver(x_returned).solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.status, result.x) == (status_expected, x_returned)
    assert result.n_fevals == 3  # The far-away evaluation was performed, not refused.


def test_a_non_finite_x_maps_to_diverged():
    # --- act --------------------------
    result = _NanSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.status, result.x, result.n_fevals) == (SolveStatus.DIVERGED, 0.5, 2)


def test_running_out_of_budget_outside_the_interval_maps_to_diverged():
    # --- act --------------------------
    result = _StrayingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=5)

    # --- assert -----------------------
    assert (result.status, result.x, result.n_fevals) == (SolveStatus.DIVERGED, 2.0, 5)


@pytest.mark.parametrize(
    "solver, status_expected",
    [(_MidpointRepeatingSolver(), SolveStatus.FUNCTION_ERROR), (_ExcursionSolver(0.5), SolveStatus.DIVERGED)],
)  # The first fails inside the interval, the second outside; where it failed decides the status.
def test_a_function_error_is_classified_by_where_it_happened(solver, status_expected):
    # --- arrange ----------------------
    def f(x: float) -> float:
        return _increasing(x) if x in (0.0, 1.0) else math.nan  # Fails anywhere but at the interval bounds.

    # --- act --------------------------
    result = solver.solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is status_expected
    assert result.n_fevals == 3  # The failing evaluation counts.


@pytest.mark.parametrize(
    "x_failing, status_expected", [(0.0, SolveStatus.FUNCTION_ERROR), (1.0, SolveStatus.FUNCTION_ERROR)]
)  # A failure at either interval bound is recorded, not raised; the midpoint is the best estimate there is.
def test_a_failure_at_an_interval_bound_is_recorded(x_failing, status_expected):
    # --- arrange ----------------------
    def f(x: float) -> float:
        return math.nan if x == x_failing else _increasing(x)

    # --- act --------------------------
    result = _RecordingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert (result.status, result.x) == (status_expected, 0.5)
    assert result.n_fevals == (1 if x_failing == 0.0 else 2)


def test_a_budget_below_the_two_interval_bound_evaluations_maps_to_max_fevals():
    # --- act --------------------------
    result = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=1)

    # --- assert -----------------------
    assert (result.status, result.x, result.n_fevals) == (SolveStatus.MAX_FEVALS, 0.5, 1)


def test_solver_exception_maps_to_solver_error():
    # --- act --------------------------
    result = _BuggySolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)

    # --- assert -----------------------
    assert result.status is SolveStatus.SOLVER_ERROR
    assert result.x == 0.5


# ==================================================================================================
#  Result fields
# ==================================================================================================
def test_history_is_none_unless_requested():
    # --- act --------------------------
    off = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10)
    on = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert off.history is None
    assert on.history == ((0.0, -0.25), (1.0, 0.75))


def test_everything_inside_the_counting_context_is_counted_and_result_x_is_a_plain_float():
    # --- act --------------------------
    result = _RecordingSolver().solve(_increasing, 0.0, 1.0, xtol=1e-3, max_fevals=3)

    # --- assert -----------------------
    # 2 zero checks + 2 sign checks on f(a), f(b); the initial x_best midpoint. The divergence checks are uncounted.
    assert result.flop_counts == FlopCounts(COMP=4, ADD=1, MUL=1)
    assert type(result.x) is float


@pytest.mark.parametrize(
    "f, n_comparisons", [(lambda x: x, 1), (lambda x: x - 1.0, 2)]
)  # A zero at a needs 1 check, a zero at b needs 2.
def test_an_early_exit_reports_the_comparisons_that_produced_it(f, n_comparisons):
    # --- act --------------------------
    result = _RecordingSolver().solve(f, 0.0, 1.0, xtol=1e-3, max_fevals=3)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.flop_counts == FlopCounts(COMP=n_comparisons)
