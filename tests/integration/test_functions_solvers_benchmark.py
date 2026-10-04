"""These tests run the benchmark engine end to end through the public API: Bisection against Regula Falsi on a
polynomial, then a summary per solver.

These tests check that the runner, the correctness check and the aggregation work together, not how well the solvers
perform, so the run uses the smallest Monte Carlo tuple set size and solves in the test process, with no worker
processes. The runner, the correctness check and the aggregation each have their own unit tests.
"""

from pathlib import Path

import polars as pl
import pytest

import sunnbear.functions as functions  # Import the module, so that pytest does not collect the `TestFunction` class.
from sunnbear.benchmark import (
    MAX_FEVALS_FACTOR,
    N_BISECTION_FEVALS,
    RESULTS_SCHEMA,
    MCTuplesSize,
    add_derived_results,
    compute_xtol_range,
    is_solution_correct,
    load_results,
    run_benchmark,
    summarize_results,
)
from sunnbear.solvers import SolverConfigRegistry, SolveStatus
from sunnbear.stats import gpq

SOLVER_IDS = ("bisection", "regula_falsi")


@pytest.fixture(scope="module")
def cubic() -> functions.TestFunction:
    """Return the shipped cubic, ``x^3 - 0.2 x - c`` on ``[-2, 2]``, calibrated to a range of ``c``."""
    return functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(c_min=-1.0, c_max=1.0)


@pytest.fixture(scope="module")
def run_dir(cubic: functions.TestFunction, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Return the directory of a run of both solvers on the cubic."""
    run_dir = tmp_path_factory.mktemp("run")
    run_benchmark(
        solver_configs=[SolverConfigRegistry.config_from_id(solver_id) for solver_id in SOLVER_IDS],
        functions=[cubic],
        run_dir=run_dir,
        mc_size=MCTuplesSize.SIZE_32,
        n_workers=1,
    )
    return run_dir


def test_the_run_solves_every_sample_with_every_solver_within_the_xtol_range(run_dir, cubic):
    """The results hold 1 row per solver and sample with the columns of `RESULTS_SCHEMA`, every `xtol` within the range
    from `compute_xtol_range` for the cubic's interval at the default evaluation count, every `c` within the calibrated
    c-range, and the default evaluation budget."""
    # --- arrange ----------------------
    results = load_results(run_dir).collect()

    # --- act --------------------------
    xtol_min, xtol_max = compute_xtol_range(a=cubic.a, b=cubic.b, n_bisection_fevals=N_BISECTION_FEVALS)

    # --- assert -----------------------
    assert dict(results.schema) == RESULTS_SCHEMA
    assert results.height == len(SOLVER_IDS) * MCTuplesSize.SIZE_32
    assert results["max_fevals"].unique().to_list() == [MAX_FEVALS_FACTOR * N_BISECTION_FEVALS]
    assert results["solver_id"].unique(maintain_order=True).to_list() == list(SOLVER_IDS)
    assert results["function_id"].unique().to_list() == [str(cubic.id)]
    assert ((results["xtol"] >= xtol_min) & (results["xtol"] < xtol_max)).all()
    assert ((results["c"] >= cubic.c_min) & (results["c"] <= cubic.c_max)).all()


def test_bisection_spends_exactly_n_bisection_fevals_and_is_correct_on_every_sample(run_dir, cubic):
    """Bisection converges on every sample in exactly `n_bisection_fevals` evaluations, since the `xtol` range is
    derived from that count, and each of bisection's answers, already checked during the run, still passes
    `is_solution_correct` when the check is repeated without `x_candidates`, the x-values at which the solver evaluated
    the function."""
    # --- arrange ----------------------
    results = load_results(run_dir).collect()
    bisection_rows = results.filter(pl.col("solver_id") == "bisection")

    # --- act --------------------------
    is_correct_again_by_row = [
        is_solution_correct(f=cubic.build_x_fun(row["c"]), x_found=row["x_found"], xtol=row["xtol"], seed=0)
        for row in bisection_rows.iter_rows(named=True)
    ]

    # --- assert -----------------------
    assert bisection_rows["status"].unique().to_list() == [SolveStatus.CONVERGED.value]
    assert bisection_rows["is_correct"].all()
    assert bisection_rows["n_fevals"].unique().to_list() == [N_BISECTION_FEVALS]
    assert all(is_correct_again_by_row)


def test_the_summary_per_solver_follows_from_the_derived_results(run_dir):
    """The summary, computed on a lazy frame from `load_results`, has 1 row per solver in run order, each with the
    solver's converged and correct fractions and its `n_fevals_eff` geometric pseudo-quantile (`gpq`) at level 0.5,
    equal to `sunnbear.stats.gpq` over that solver's `n_fevals_eff` values."""
    # --- arrange ----------------------
    derived_results = add_derived_results(load_results(run_dir))
    n_fevals_eff_by_solver_id = {
        solver_id: derived_results.filter(pl.col("solver_id") == solver_id).collect()["n_fevals_eff"].to_list()
        for solver_id in SOLVER_IDS
    }

    # --- act --------------------------
    summary = summarize_results(derived_results, "solver_id").collect()

    # --- assert -----------------------
    assert summary["solver_id"].to_list() == list(SOLVER_IDS)
    bisection_summary, regula_falsi_summary = summary.rows(named=True)
    assert bisection_summary["converged_fraction"] == 1.0
    assert bisection_summary["correct_fraction"] == 1.0
    assert regula_falsi_summary["correct_fraction"] <= regula_falsi_summary["converged_fraction"]
    assert summary["n_fevals_eff_gpq_50"].to_list() == pytest.approx(
        [gpq(n_fevals_eff_by_solver_id[solver_id], 0.5) for solver_id in SOLVER_IDS]
    )
