"""These tests run the benchmark engine end to end through the public API: Bisection against Regula Falsi on a
polynomial, then a summary per solver.

The run is the smallest one the engine accepts, 32 Monte Carlo samples solved in this process, so the layers'
contracts are under test, not the solvers' strength; the runner, the correctness check and the aggregation each
have their own tests under `tests/benchmark/`.
"""

import polars as pl
import pytest

import sunnbear.functions as functions  # The module, so pytest does not try to collect the `TestFunction` class.
from sunnbear.benchmark import (
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
N_BISECTION_FEVALS = 40


@pytest.fixture(scope="module")
def cubic() -> functions.TestFunction:
    """Return the shipped cubic, ``x^3 - 0.2 x - c`` on ``[-2, 2]``, calibrated to ``c`` in ``[-1, 1]``."""
    return functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(c_min=-1.0, c_max=1.0)


@pytest.fixture(scope="module")
def results(cubic: functions.TestFunction, tmp_path_factory: pytest.TempPathFactory) -> pl.DataFrame:
    """Run both solvers on the cubic over the 32 samples of the smallest size, in this process, and return the results."""
    run_dir = tmp_path_factory.mktemp("run")
    run_benchmark(
        solver_configs=[SolverConfigRegistry.config_from_id(solver_id) for solver_id in SOLVER_IDS],
        functions=[cubic],
        run_dir=run_dir,
        mc_size=MCTuplesSize.SIZE_32,
        n_bisection_fevals=N_BISECTION_FEVALS,
        n_workers=1,
    )
    return load_results(run_dir).collect()


def test_the_run_solves_every_sample_with_every_solver_within_the_xtol_range(results, cubic):
    """The results hold 1 row per solver and sample, every `xtol` within the range that `compute_xtol_range` gives for
    the cubic's interval, and every `c` within the calibrated c-range."""
    # --- act --------------------------
    xtol_min, xtol_max = compute_xtol_range(a=cubic.a, b=cubic.b, n_bisection_fevals=N_BISECTION_FEVALS)

    # --- assert -----------------------
    assert results.height == len(SOLVER_IDS) * MCTuplesSize.SIZE_32
    assert results["solver_id"].unique(maintain_order=True).to_list() == list(SOLVER_IDS)
    assert results["function_id"].unique().to_list() == [str(cubic.id)]
    assert ((results["xtol"] >= xtol_min) & (results["xtol"] < xtol_max)).all()
    assert ((results["c"] >= cubic.c_min) & (results["c"] <= cubic.c_max)).all()


def test_bisection_spends_exactly_n_bisection_fevals_and_is_correct_on_every_sample(results, cubic):
    """Bisection converges on every sample in exactly `n_bisection_fevals` evaluations, the count that the `xtol` range
    is built for, and its answers pass `is_solution_correct` again, without the solve's own x-values."""
    # --- arrange ----------------------
    bisection_rows = results.filter(pl.col("solver_id") == "bisection")

    # --- act --------------------------
    is_correct_again = [
        is_solution_correct(f=cubic.build_x_fun(row["c"]), x_found=row["x_found"], xtol=row["xtol"], seed=0)
        for row in bisection_rows.iter_rows(named=True)
    ]

    # --- assert -----------------------
    assert bisection_rows["status"].unique().to_list() == [SolveStatus.CONVERGED.value]
    assert bisection_rows["is_correct"].all()
    assert bisection_rows["n_fevals"].unique().to_list() == [N_BISECTION_FEVALS]
    assert all(is_correct_again)


def test_the_summary_per_solver_follows_from_the_derived_results(results):
    """The summary, computed lazily, has 1 row per solver in run order; bisection's fractions are 1 and its `gpq` is its
    constant evaluation count, and regula falsi's `gpq` equals `sunnbear.stats.gpq` over its own derived counts."""
    # --- arrange ----------------------
    derived = add_derived_results(results.lazy())
    regula_falsi_n_fevals_eff = derived.filter(pl.col("solver_id") == "regula_falsi").collect()["n_fevals_eff"]

    # --- act --------------------------
    summary = summarize_results(derived, "solver_id").collect()

    # --- assert -----------------------
    assert summary["solver_id"].to_list() == list(SOLVER_IDS)
    bisection, regula_falsi = summary.rows(named=True)
    assert bisection["converged_fraction"] == 1.0
    assert bisection["correct_fraction"] == 1.0
    assert bisection["n_fevals_eff_gpq_50"] == pytest.approx(N_BISECTION_FEVALS)
    assert regula_falsi["correct_fraction"] <= regula_falsi["converged_fraction"]
    assert regula_falsi["n_fevals_eff_gpq_50"] == pytest.approx(gpq(regula_falsi_n_fevals_eff.to_list(), 0.5))
