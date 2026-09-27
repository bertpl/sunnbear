"""`BenchmarkTask` gives 1 row per sample and solver, checks every converged answer only, and pickles as it is."""

import pickle

import polars as pl
import pytest
from counted_float import FlopType

import sunnbear.functions as functions  # Import the module, so pytest does not try to collect `TestFunction`.
from sunnbear._core.benchmark import task
from sunnbear._core.benchmark.mc_tuples import load_mc_tuples
from sunnbear._core.benchmark.results_schema import RESULTS_SCHEMA, flop_count_column_name
from sunnbear._core.benchmark.run_settings import BenchmarkRunSettings
from sunnbear._core.benchmark.task import BenchmarkTask
from sunnbear._core.benchmark.tolerances import compute_xtol_range
from sunnbear.solvers import Solver, SolverConfig, SolverConfigRegistry, SolverRole, SolveState, SolveStatus

N_BISECTION_FEVALS = 40
SIZE = 32


# ==================================================================================================
#  Test-local solvers and fixtures
# ==================================================================================================
class _UnevaluatedMidpointSolver(Solver):
    """`_UnevaluatedMidpointSolver` reports the unevaluated midpoint as converged: a wrong answer on the test cubic."""

    name = "unevaluated_midpoint"
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
def unevaluated_midpoint_and_stalling_configs(isolated_solver_config_registry) -> tuple[SolverConfig, SolverConfig]:
    """Return configs of `_UnevaluatedMidpointSolver` and `_StallingSolver`, registered only for the test."""

    class _UnevaluatedMidpointConfig(SolverConfig):
        solver_cls = _UnevaluatedMidpointSolver
        role = SolverRole.USER_OTHER

    class _StallingConfig(SolverConfig):
        solver_cls = _StallingSolver
        role = SolverRole.USER_OTHER

    return SolverConfigRegistry.config_from_id("unevaluated_midpoint"), SolverConfigRegistry.config_from_id("stalling")


def _task_on_cubic(cubic: functions.TestFunction, solver_configs) -> BenchmarkTask:
    """Return the benchmark task on the cubic with the first `SIZE` shipped Monte Carlo tuples."""
    return BenchmarkTask.from_test_function(
        function=cubic,
        solver_configs=solver_configs,
        run_settings=BenchmarkRunSettings(mc_size=SIZE, n_bisection_fevals=N_BISECTION_FEVALS, root_seed=1),
    )


def _run_task_on_cubic(cubic: functions.TestFunction, solver_configs) -> pl.DataFrame:
    """Run the benchmark task on the cubic with the first `SIZE` shipped Monte Carlo tuples."""
    return _task_on_cubic(cubic, solver_configs).run()


# ==================================================================================================
#  Rows and schema
# ==================================================================================================
def test_a_task_gives_1_row_per_sample_and_solver_in_the_results_schema(cubic):
    """The rows follow `RESULTS_SCHEMA`, sample by sample, with `xtol` in its range and `c` in `[c_min, c_max]`."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id("bisection"), SolverConfigRegistry.config_from_id("regula_falsi")]
    xtol_min, xtol_max = compute_xtol_range(a=cubic.a, b=cubic.b, n_bisection_fevals=N_BISECTION_FEVALS)
    mc_tuples = load_mc_tuples(SIZE)

    # --- act --------------------------
    results = _run_task_on_cubic(cubic, configs)

    # --- assert -----------------------
    assert dict(results.schema) == RESULTS_SCHEMA
    assert results.null_count().sum_horizontal().item() == 0  # run_benchmark_task fills every schema column.
    assert results["solver_id"].to_list() == ["bisection", "regula_falsi"] * SIZE
    assert results["mc_sample_idx"].to_list() == [i for i in range(SIZE) for _ in configs]
    assert set(results["function_id"]) == {"f2.1.1[p1=0.2]"}
    assert set(results["mc_size"]) == {SIZE}
    assert results["u"].to_list()[::2] == mc_tuples.u.tolist()
    assert results["xtol"].is_between(xtol_min, xtol_max, closed="left").all()
    assert results["c"].is_between(cubic.c_min, cubic.c_max).all()


def test_bisection_is_correct_in_exactly_n_bisection_fevals_with_counted_flops(cubic):
    """Every bisection solve is correct in exactly `N_BISECTION_FEVALS` evaluations, with its flops counted."""
    # --- act --------------------------
    results = _run_task_on_cubic(cubic, [SolverConfigRegistry.config_from_id("bisection")])

    # --- assert -----------------------
    assert (results["status"] == SolveStatus.CONVERGED.value).all()
    assert results["is_correct"].all()
    assert (results["n_fevals"] == N_BISECTION_FEVALS).all()
    assert (results["wall_time_ns"] > 0).all()
    assert (results[flop_count_column_name(FlopType.COMP)] > 0).all()


# ==================================================================================================
#  Correctness checks
# ==================================================================================================
def test_a_converged_but_wrong_answer_is_not_correct(cubic, unevaluated_midpoint_and_stalling_configs):
    """A solve that reports the unevaluated midpoint as converged is not correct: no root lies within `xtol`."""
    # --- arrange ----------------------
    unevaluated_midpoint_config, _ = unevaluated_midpoint_and_stalling_configs

    # --- act --------------------------
    results = _run_task_on_cubic(cubic, [unevaluated_midpoint_config])

    # --- assert -----------------------
    assert (results["status"] == SolveStatus.CONVERGED.value).all()
    assert not results["is_correct"].any()


def test_only_converged_solves_are_checked_with_the_evaluated_x_values_as_candidates(
    cubic, unevaluated_midpoint_and_stalling_configs, monkeypatch
):
    """The check runs once per converged solve, never for a solve out of budget, and receives the evaluated x-values."""
    # --- arrange ----------------------
    calls = []

    def is_solution_correct_spy(**kwargs) -> bool:
        calls.append(kwargs)
        return True

    monkeypatch.setattr(task, "is_solution_correct", is_solution_correct_spy)
    _, stalling_config = unevaluated_midpoint_and_stalling_configs
    configs = [SolverConfigRegistry.config_from_id("bisection"), stalling_config]

    # --- act --------------------------
    results = _run_task_on_cubic(cubic, configs)

    # --- assert -----------------------
    stalling_rows = results.filter(pl.col("solver_id") == "stalling")
    assert (stalling_rows["status"] == SolveStatus.MAX_FEVALS.value).all()
    assert not stalling_rows["is_correct"].any()
    assert len(calls) == SIZE  # The check runs once per bisection solve.
    assert all(call["x_candidates"][:2] == (cubic.a, cubic.b) for call in calls)  # A solve evaluates a and b first.
    assert all(len(call["x_candidates"]) == N_BISECTION_FEVALS for call in calls)


def test_a_task_holds_only_ids_and_survives_pickling(cubic):
    """A task holds the ids of its function and solvers, and a pickled copy, as a worker receives it, runs alike."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id("bisection")]
    task_on_cubic = _task_on_cubic(cubic, configs)

    # --- act --------------------------
    task_copy = pickle.loads(pickle.dumps(task_on_cubic))  # noqa: S301 — the data is this test's own

    # --- assert -----------------------
    assert (task_copy.function_id, task_copy.solver_ids) == ("f2.1.1[p1=0.2]", ("bisection",))
    assert task_copy == task_on_cubic
    assert task_copy.run().drop("wall_time_ns").equals(task_on_cubic.run().drop("wall_time_ns"))


def test_a_task_is_reproducible_apart_from_wall_time(cubic):
    """The same inputs give the same rows; only the measured wall time differs."""
    # --- arrange ----------------------
    configs = [SolverConfigRegistry.config_from_id("bisection"), SolverConfigRegistry.config_from_id("regula_falsi")]

    # --- act --------------------------
    first, second = _run_task_on_cubic(cubic, configs), _run_task_on_cubic(cubic, configs)

    # --- assert -----------------------
    assert first.drop("wall_time_ns").equals(second.drop("wall_time_ns"))
