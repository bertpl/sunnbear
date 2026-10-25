"""The tests of `run_stages` check that:

- each stage runs on the output table of the stage before it, and its output table, reports and manifest are
  written into the workspace, which reads the reports back;
- a rerun replaces them;
- a stage that breaks a rule of the chain stops the run before its output is written;
- a stage that runs tasks in the worker pool gives the same output with 1 or 2 workers.
"""

import hashlib

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.core.manifest import PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.core.stage_runner import run_stages
from sunnbear._core.benchmark.suites.pipeline.core.workspace import PipelineWorkspace
from sunnbear._core.utils.worker_pool import WorkerPool

from .example_stages import (
    ExampleColumnDroppingStage,
    ExampleIdlessStage,
    ExampleNumbersStage,
    ExampleRowAddingStage,
    ExampleRowDuplicatingStage,
    ExampleSmallNumbersStage,
    ExampleSquaresStage,
)

# A pool with 1 worker runs its tasks in this process and needs no with block.
_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)

# These are the files that a run of the 2 stages that follow the rules writes, relative to the workspace directory.
_WORKSPACE_FILES = [
    "manifests/s1_numbers.json",
    "manifests/s2_small_numbers.json",
    "reports/s2_small_numbers/large_numbers.parquet",
    "s1_numbers.parquet",
    "s2_small_numbers.parquet",
]


def test_each_stage_runs_on_the_table_before_it_and_its_files_are_written(tmp_path):
    """Each stage's output table extends the table before it; the manifest matches the bytes of the output table and
    of each report, and records the output table before it."""
    # --- act --------------------------
    manifests = run_stages(
        PipelineWorkspace(tmp_path),
        [ExampleNumbersStage(), ExampleSmallNumbersStage()],
        worker_pool=_IN_PROCESS_WORKER_POOL,
    )

    # --- assert -----------------------
    numbers_manifest, small_numbers_manifest = manifests
    for manifest in manifests:
        output_file = tmp_path / f"{manifest.output_name}.parquet"
        manifest_file = tmp_path / "manifests" / f"{manifest.output_name}.json"
        assert hashlib.sha256(output_file.read_bytes()).hexdigest() == manifest.output_sha256
        assert PipelineStageManifest.model_validate_json(manifest_file.read_text()) == manifest
    report_file = tmp_path / "reports" / "s2_small_numbers" / "large_numbers.parquet"
    assert small_numbers_manifest.report_sha256s == {
        "large_numbers": hashlib.sha256(report_file.read_bytes()).hexdigest()
    }
    assert pl.read_parquet(tmp_path / "s2_small_numbers.parquet").rows() == [("n1", 1.0, 2.0), ("n2", 2.0, 4.0)]
    assert PipelineWorkspace(tmp_path).read_report("s2_small_numbers", "large_numbers").rows() == [("n3", 3.0)]
    assert small_numbers_manifest.input_sha256 == numbers_manifest.output_sha256
    assert (small_numbers_manifest.n_rows, small_numbers_manifest.n_dropped_rows) == (2, 1)


def test_a_rerun_replaces_the_files_and_leaves_no_temporary_files(tmp_path):
    """A second run into the same workspace replaces every file of the first, and leaves only the final files."""
    # --- arrange ----------------------
    workspace = PipelineWorkspace(tmp_path)
    run_stages(workspace, [ExampleNumbersStage(), ExampleSmallNumbersStage()], worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- act --------------------------
    second_manifests = run_stages(
        workspace, [ExampleNumbersStage(), ExampleSmallNumbersStage()], worker_pool=_IN_PROCESS_WORKER_POOL
    )

    # --- assert -----------------------
    assert [
        PipelineStageManifest.model_validate_json((tmp_path / "manifests" / f"{name}.json").read_text())
        for name in ("s1_numbers", "s2_small_numbers")
    ] == list(second_manifests)
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.*")) == _WORKSPACE_FILES


@pytest.mark.parametrize(
    "stages, message",
    [
        pytest.param([ExampleIdlessStage()], r"ExampleIdlessStage outputs a table without a problem_id", id="no_id"),
        pytest.param(
            [ExampleNumbersStage(), ExampleRowDuplicatingStage()],
            r"ExampleRowDuplicatingStage outputs a table that holds a problem_id more than once",
            id="duplicated_rows",
        ),
        pytest.param(
            [ExampleNumbersStage(), ExampleColumnDroppingStage()],
            r"ExampleColumnDroppingStage drops the columns \['x'\]",
            id="dropped_column",
        ),
        pytest.param(
            [ExampleNumbersStage(), ExampleRowAddingStage()],
            r"ExampleRowAddingStage outputs rows that the table before it does not hold",
            id="added_row",
        ),
    ],
)
def test_a_stage_that_breaks_a_rule_of_the_chain_stops_the_run(tmp_path, stages, message):
    """A stage whose output table breaks a rule of the chain raises `ValueError`, which names the stage and the rule,
    and its output table is not written."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        run_stages(PipelineWorkspace(tmp_path), stages, worker_pool=_IN_PROCESS_WORKER_POOL)
    assert not (tmp_path / f"{stages[-1].output_name}.parquet").exists()


def test_a_stage_that_runs_tasks_in_the_worker_pool_gives_the_same_output_with_1_or_2_workers(tmp_path):
    """A stage whose tasks run in this process or in 2 workers writes the same output file; each manifest records its
    run's number of workers."""
    # --- act --------------------------
    squares_manifests = []
    for n_workers in (1, 2):
        with WorkerPool(n_workers=n_workers) as worker_pool:
            manifests = run_stages(
                PipelineWorkspace(tmp_path / f"{n_workers}_workers"),
                [ExampleNumbersStage(), ExampleSquaresStage()],
                worker_pool=worker_pool,
            )
        squares_manifests.append(manifests[-1])

    # --- assert -----------------------
    in_process_manifest, worker_processes_manifest = squares_manifests
    assert worker_processes_manifest.output_sha256 == in_process_manifest.output_sha256
    assert (in_process_manifest.n_workers, worker_processes_manifest.n_workers) == (1, 2)
    squares = pl.read_parquet(tmp_path / "2_workers" / "s2_squares.parquet")
    assert squares["squared_x"].to_list() == [1.0, 4.0, 9.0]
