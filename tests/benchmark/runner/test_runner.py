"""`run_benchmark` writes 1 results file per formula, in worker processes or not, resumes a crashed run, and refuses to
resume another run.
"""

from pathlib import Path

import polars as pl
import pytest

import sunnbear.functions as functions  # Import the module, so pytest does not try to collect `TestFunction`.
from sunnbear._core.benchmark.runner.exceptions import BenchmarkRunError
from sunnbear._core.benchmark.runner.results_schema import RESULTS_SCHEMA
from sunnbear._core.benchmark.runner.run_dir import BenchmarkRunDir
from sunnbear._core.benchmark.runner.runner import load_results, run_benchmark
from sunnbear._core.benchmark.runner.task import BenchmarkTask
from sunnbear.solvers import SolverConfigRegistry

MC_SIZE = 32


# ==================================================================================================
#  Fixtures
# ==================================================================================================
# The test functions of the 2 formulas alternate in the list, so the tests check that the run groups them by
# formula: both test functions of f2.1.1 run first.
_FUNCTION_IDS = ("f2.1.1[p1=0.2]", "f2.1.2[p1=3.0]", "f2.1.1[p1=0.4]")
_SOLVER_IDS = ("bisection", "regula_falsi")


def _run_inputs(run_dir: Path, **changes: object) -> dict[str, object]:
    """Return the keyword arguments of a small run into `run_dir` in this process, with `changes` applied.

    The run stays in this process, so a test can replace `BenchmarkTask.run` with `monkeypatch`.
    """
    return {
        "solver_configs": [SolverConfigRegistry.config_from_id(solver_id) for solver_id in _SOLVER_IDS],
        "functions": [
            functions.FormulaRegistry.candidate_from_id(function_id).calibrated(-1.0, 1.0)
            for function_id in _FUNCTION_IDS
        ],
        "run_dir": run_dir,
        "root_seed": 1,
        "mc_size": MC_SIZE,
        "n_workers": 1,
    } | changes


@pytest.fixture(scope="module")
def finished_run_dir(tmp_path_factory) -> Path:
    """Return the run directory of a finished small run."""
    run_dir = tmp_path_factory.mktemp("finished_run")
    run_benchmark(**_run_inputs(run_dir))
    return run_dir


def _results_without_wall_time(run_dir: Path) -> pl.DataFrame:
    """Return the run's results without `wall_time_ns`, the only column that differs between 2 identical runs."""
    return load_results(run_dir).drop("wall_time_ns").collect()


# ==================================================================================================
#  Running
# ==================================================================================================
def test_a_run_writes_1_results_file_per_formula_and_loads_every_solve(finished_run_dir):
    """A finished run holds its run info and 1 results file per formula, and loads 1 row per solve in run order."""
    # --- act --------------------------
    results = load_results(finished_run_dir).collect()

    # --- assert -----------------------
    assert sorted(path.name for path in finished_run_dir.iterdir()) == [
        "f2.1.1.parquet",
        "f2.1.2.parquet",
        "run_info.json",
    ]
    assert dict(results.schema) == RESULTS_SCHEMA
    assert results.height == len(_FUNCTION_IDS) * len(_SOLVER_IDS) * MC_SIZE
    assert results["function_id"].unique(maintain_order=True).to_list() == [
        "f2.1.1[p1=0.2]",
        "f2.1.1[p1=0.4]",
        "f2.1.2[p1=3.0]",
    ]


def test_a_run_in_worker_processes_gives_the_results_of_a_run_in_this_process(finished_run_dir, tmp_path):
    """With 2 workers, the tasks finish in any order, but the results files hold the same rows in the same order."""
    # --- act --------------------------
    run_benchmark(**_run_inputs(tmp_path, n_workers=2))

    # --- assert -----------------------
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(path.name for path in finished_run_dir.iterdir())
    assert _results_without_wall_time(tmp_path).equals(_results_without_wall_time(finished_run_dir))


def test_resuming_a_finished_run_changes_nothing(finished_run_dir, monkeypatch):
    """Resuming a finished run runs no task and leaves its files as they were."""
    # --- arrange ----------------------
    file_contents_before = {path.name: path.read_bytes() for path in finished_run_dir.iterdir()}

    def fail_if_run(self: BenchmarkTask) -> pl.DataFrame:
        raise AssertionError(f"Task on {self.function_id} ran again.")

    monkeypatch.setattr(BenchmarkTask, "run", fail_if_run)

    # --- act --------------------------
    run_benchmark(**_run_inputs(finished_run_dir))

    # --- assert -----------------------
    assert {path.name: path.read_bytes() for path in finished_run_dir.iterdir()} == file_contents_before


def test_a_crashed_run_resumes_with_only_its_unfinished_tasks(finished_run_dir, tmp_path, monkeypatch):
    """After a crash in the 2nd task, resuming runs only the 2 tasks without staged results, and the results match."""
    # --- arrange ----------------------
    run_task = BenchmarkTask.run
    function_ids_run: list[str] = []
    is_crashing_on_2nd_task = True

    def run_and_crash_on_2nd_task(self: BenchmarkTask) -> pl.DataFrame:
        function_ids_run.append(self.function_id)
        if is_crashing_on_2nd_task and len(function_ids_run) == 2:
            raise RuntimeError("crash")
        return run_task(self)

    monkeypatch.setattr(BenchmarkTask, "run", run_and_crash_on_2nd_task)
    with pytest.raises(RuntimeError, match="crash"):
        run_benchmark(**_run_inputs(tmp_path))
    with pytest.raises(BenchmarkRunError, match="not finished"):
        load_results(tmp_path)
    function_ids_run.clear()
    is_crashing_on_2nd_task = False

    # --- act --------------------------
    run_benchmark(**_run_inputs(tmp_path))

    # --- assert -----------------------
    # The 1st task's results were staged before the crash, so only the crashed task and the next one run.
    assert function_ids_run == ["f2.1.1[p1=0.4]", "f2.1.2[p1=3.0]"]
    assert _results_without_wall_time(tmp_path).equals(_results_without_wall_time(finished_run_dir))


def test_a_run_that_stopped_before_writing_a_formula_file_writes_it_from_the_staged_results(
    finished_run_dir, tmp_path, monkeypatch
):
    """A run that staged all of a formula's results but crashed before writing its file only writes the file."""
    # --- arrange ----------------------
    write_formula_results = BenchmarkRunDir.write_formula_results

    def crash(self: BenchmarkRunDir, formula_id: str, n_functions: int) -> None:
        raise RuntimeError("crash")

    monkeypatch.setattr(BenchmarkRunDir, "write_formula_results", crash)
    with pytest.raises(RuntimeError, match="crash"):
        run_benchmark(**_run_inputs(tmp_path))
    monkeypatch.setattr(BenchmarkRunDir, "write_formula_results", write_formula_results)
    run_task = BenchmarkTask.run
    function_ids_run: list[str] = []

    def record_and_run(self: BenchmarkTask) -> pl.DataFrame:
        function_ids_run.append(self.function_id)
        return run_task(self)

    monkeypatch.setattr(BenchmarkTask, "run", record_and_run)

    # --- act --------------------------
    run_benchmark(**_run_inputs(tmp_path))

    # --- assert -----------------------
    # Both test functions of f2.1.1 were staged before the crash, so only f2.1.2's task runs.
    assert function_ids_run == ["f2.1.2[p1=3.0]"]
    assert _results_without_wall_time(tmp_path).equals(_results_without_wall_time(finished_run_dir))


@pytest.mark.parametrize(
    "changes, differing_field",
    [
        ({"root_seed": 2}, "run_settings"),
        ({"mc_size": 64}, "run_settings"),
        ({"solver_configs": [SolverConfigRegistry.config_from_id("bisection")]}, "solver_versions"),
        (
            {"functions": [functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(-0.5, 0.5)]},
            "function_infos",
        ),
    ],
)
def test_resuming_with_other_inputs_is_refused(finished_run_dir, changes, differing_field):
    """A run directory only resumes with the inputs of the run that it holds, and the error names what differs."""
    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match=differing_field):
        run_benchmark(**_run_inputs(finished_run_dir, **changes))


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"solver_configs": []}, "solver_configs must hold at least 1 item"),
        ({"functions": []}, "functions must hold at least 1 item"),
        (
            {"functions": [functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(-1.0, 1.0)] * 2},
            r"functions holds these ids more than once: \['f2.1.1\[p1=0.2\]'\]",
        ),
        ({"mc_size": 33}, "size must be one of"),
        ({"n_bisection_fevals": 1}, "n_bisection_fevals must be at least 2"),
        ({"n_workers": 0}, "n_workers must be at least 1"),
    ],
)
def test_invalid_inputs_are_refused_before_the_run_dir_is_written(tmp_path, changes, message):
    """Invalid inputs raise `ValueError` and leave the run directory unwritten."""
    # --- arrange ----------------------
    run_dir = tmp_path / "run"

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        run_benchmark(**_run_inputs(run_dir, **changes))
    assert not run_dir.exists()


def test_loading_a_run_dir_without_a_run_is_refused(tmp_path):
    """`load_results` on a directory that holds no run raises `BenchmarkRunError`."""
    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match="holds no benchmark run"):
        load_results(tmp_path)
