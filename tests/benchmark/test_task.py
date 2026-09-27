"""`run_benchmark_task` gives 1 row per sample and solver, and checks exactly the converged answers."""

import polars as pl
import pytest
from counted_float import FlopType

import sunnbear.functions as functions  # The module, so pytest does not try to collect the `TestFunction` class.
from sunnbear._core.benchmark import task
from sunnbear._core.benchmark.mc_tuples import load_mc_tuples
from sunnbear._core.benchmark.results_schema import RESULTS_SCHEMA, flops_column_name
from sunnbear._core.benchmark.task import run_benchmark_task
from sunnbear._core.benchmark.tolerances import compute_xtol_range
from sunnbear.solvers import Solver, SolverConfig, SolverConfigRegistry, SolverRole, SolveState, SolveStatus

N_BISECTION_FEVALS = 40
SIZE = 32


# ==================================================================================================
#  Test-local solvers and fixtures
# ==================================================================================================
class _MidpointSolver(Solver):
    """`_MidpointSolver` reports the interval's midpoint as converged without evaluating it, a wrong answer."""

    name = "midpoint"
    version = 1

    def _solve(self, state: SolveState) -> float:
        return state.x_best


class _StallingSolver(Solver):
    """`_StallingSolver` evaluates the midpoint over and over, so every solve runs out of budget."""

    name = "stalling"
    version = 1

    def _solve(self, state: SolveState) -> float:
        while True:
            state.f(state.x_best)


@pytest.fixture(scope="module")
def cubic() -> functions.TestFunction:
    """Return the shipped cubic, ``x^3 - 0.2 x - c`` on ``[-2, 2]``, calibrated to ``c`` in ``[-1, 1]``."""
    return functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(c_min=-1.0, c_max=1.0)


@pytest.fixture
def test_local_configs(isolated_solver_config_registry) -> tuple[SolverConfig, SolverConfig]:
    """Return configs of `_MidpointSolver` and `_StallingSolver`, registered only for the test."""

    class _MidpointConfig(SolverConfig):
        solver_cls = _MidpointSolver
        role = SolverRole.USER_OTHER

    class _StallingConfig(SolverConfig):
        solver_cls = _StallingSolver
        role = SolverRole.USER_OTHER

    return SolverConfigRegistry.config_from_id("midpoint"), SolverConfigRegistry.config_from_id("stalling")


def _run(cubic: functions.TestFunction, solver_configs, root_seed: int = 1) -> pl.DataFrame:
    """Run the task on the cubic with the first `SIZE` shipped tuples."""
    return run_benchmark_task(
        function=cubic,
        solver_configs=solver_configs,
        mc_tuples=load_mc_tuples(SIZE),
        n_bisection_fevals=N_BISECTION_FEVALS,
        root_seed=root_seed,
    )


# ==================================================================================================
#  Rows and schema
# ==================================================================================================
def test_a_task_gives_1_row_per_sample_and_solver_in_the_results_schema(cubic):
    """The rows follow `RESULTS_SCHEMA`, sample by sample, and map each tuple into the `xtol` range and c-range."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id("bisection"), SolverConfigRegistry.config_from_id("regula_falsi")]
    xtol_min, xtol_max = compute_xtol_range(a=cubic.a, b=cubic.b, n_bisection_fevals=N_BISECTION_FEVALS)
    tuples = load_mc_tuples(SIZE)

    # --- act --------------------------
    results = _run(cubic, configs)

    # --- assert -----------------------
    assert dict(results.schema) == RESULTS_SCHEMA
    assert results["solver_id"].to_list() == ["bisection", "regula_falsi"] * SIZE
    assert results["mc_sample_idx"].to_list() == [i for i in range(SIZE) for _ in configs]
    assert set(results["function_id"]) == {"f2.1.1[p1=0.2]"}
    assert set(results["size"]) == {SIZE}
    assert results["u"].to_list()[::2] == tuples.u.tolist()
    assert results["xtol"].is_between(xtol_min, xtol_max, closed="left").all()
    assert results["c"].is_between(cubic.c_min, cubic.c_max).all()


def test_bisection_is_correct_in_exactly_n_bisection_fevals_with_counted_flops(cubic):
    """Every bisection solve converges to a correct answer in `N_BISECTION_FEVALS`, with its flops in their columns."""
    # --- act --------------------------
    results = _run(cubic, [SolverConfigRegistry.config_from_id("bisection")])

    # --- assert -----------------------
    assert (results["status"] == SolveStatus.CONVERGED.value).all()
    assert results["correct"].all()
    assert (results["n_fevals"] == N_BISECTION_FEVALS).all()
    assert (results["wall_time_ns"] > 0).all()
    assert (results[flops_column_name(FlopType.COMP)] > 0).all()


# ==================================================================================================
#  Correctness checks
# ==================================================================================================
def test_a_converged_but_wrong_answer_is_not_correct(cubic, test_local_configs):
    """The midpoint is reported as converged, but no root lies within `xtol` of it."""
    # --- arrange ----------------------
    midpoint_config, _ = test_local_configs

    # --- act --------------------------
    results = _run(cubic, [midpoint_config])

    # --- assert -----------------------
    assert (results["status"] == SolveStatus.CONVERGED.value).all()
    assert not results["correct"].any()


def test_only_converged_solves_are_checked_with_the_evaluated_x_values_as_candidates(
    cubic, test_local_configs, monkeypatch
):
    """The check runs once per converged solve, never for a solve out of budget, and receives the evaluated x-values."""
    # --- arrange ----------------------
    calls = []

    def is_solution_correct_spy(**kwargs) -> bool:
        calls.append(kwargs)
        return True

    monkeypatch.setattr(task, "is_solution_correct", is_solution_correct_spy)
    _, stalling_config = test_local_configs
    configs = [SolverConfigRegistry.config_from_id("bisection"), stalling_config]

    # --- act --------------------------
    results = _run(cubic, configs)

    # --- assert -----------------------
    stalled = results.filter(pl.col("solver_id") == "stalling")
    assert (stalled["status"] == SolveStatus.MAX_FEVALS.value).all()
    assert not stalled["correct"].any()
    assert len(calls) == SIZE  # 1 per bisection solve
    assert all(call["x_candidates"][:2] == [cubic.a, cubic.b] for call in calls)  # a solve evaluates a and b first
    assert all(len(call["x_candidates"]) == N_BISECTION_FEVALS for call in calls)


def test_a_task_is_reproducible_apart_from_wall_time(cubic):
    """The same inputs give the same rows; only the measured wall time differs."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id("bisection"), SolverConfigRegistry.config_from_id("regula_falsi")]

    # --- act --------------------------
    first, second = _run(cubic, configs), _run(cubic, configs)

    # --- assert -----------------------
    assert first.drop("wall_time_ns").equals(second.drop("wall_time_ns"))
