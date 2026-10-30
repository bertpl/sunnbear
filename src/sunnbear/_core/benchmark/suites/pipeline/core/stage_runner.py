"""`run_stages` runs the stages of the benchmark suite pipeline as a chain, and writes their outputs and manifests."""

import datetime
import time
from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from sunnbear._core.utils.worker_pool import WorkerPool

from .manifest import PipelineStageExecutionInfo, PipelineStageManifest
from .stage import PipelineStage
from .stop import PipelineStop, PipelineStopError
from .workspace import PipelineWorkspace


# ==================================================================================================
#  run_stages
# ==================================================================================================
def run_stages(
    workspace: PipelineWorkspace, stages: Sequence[PipelineStage], *, worker_pool: WorkerPool
) -> "PipelineRunResult":
    """Run `stages` in order, each on the output table of the stage before it, and have `workspace` write each output.

    The first stage receives an empty table. Every stage receives `worker_pool`, in which it may run tasks, and its
    manifest records the pool's number of workers. A `worker_pool` with more than 1 worker must be inside its ``with``
    block, which `run_stages` does not open.

    A stage that raises `PipelineStopError` stops the run: its output is not written, and the stages after it do not
    run.

    Returns:
        The manifest of each stage that wrote its output, in run order, and the `PipelineStop` of the stage that
        stopped the run, if any.

    Raises:
        ValueError: If a stage's output table breaks a rule of the chain (see `PipelineStage`): it has no unique
            ``problem_id`` per row, lacks a column of the table before it, or holds a row that the table before it
            does not hold. The stage's output is then not written.
    """
    previous_table = pl.DataFrame()
    previous_manifest: PipelineStageManifest | None = None
    manifests: list[PipelineStageManifest] = []
    for stage in stages:
        # --- output -----------------------------
        started_at = datetime.datetime.now(datetime.UTC)
        t_start = time.perf_counter()
        try:
            output = stage.compute_output(previous_table, worker_pool=worker_pool)
        except PipelineStopError as error:
            return PipelineRunResult(
                manifests=tuple(manifests), stop=PipelineStop(output_name=stage.output_name, reason=str(error))
            )
        duration_sec = time.perf_counter() - t_start
        _check_chain_rules(stage, previous_table, output.table)

        # --- output, report and manifest files --
        manifest = workspace.write_stage_output_and_manifest(
            stage=stage,
            output=output,
            input_manifest=previous_manifest,
            execution_info=PipelineStageExecutionInfo(
                started_at=started_at, duration_sec=duration_sec, n_workers=worker_pool.n_workers
            ),
        )
        manifests.append(manifest)
        previous_table, previous_manifest = output.table, manifest
    return PipelineRunResult(manifests=tuple(manifests), stop=None)


# ==================================================================================================
#  PipelineRunResult
# ==================================================================================================
@dataclass(frozen=True)
class PipelineRunResult:
    """A `PipelineRunResult` holds the manifests of a run's stages, and the stop that ended the run early, if any.

    Attributes:
        manifests: The manifest of each stage that wrote its output, in run order.
        stop: The stage that stopped the run, and why; ``None`` when every stage wrote its output.
    """

    manifests: tuple[PipelineStageManifest, ...]
    stop: PipelineStop | None


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _check_chain_rules(stage: PipelineStage, previous_table: pl.DataFrame, table: pl.DataFrame) -> None:
    """Check that the output table of `stage` extends `previous_table` as the chain requires.

    Raises:
        ValueError: If `table` has no unique ``problem_id`` per row, lacks a column of `previous_table`, or holds a
            ``problem_id`` that `previous_table` does not hold, unless `previous_table` is the first stage's empty
            input.
    """
    stage_name = type(stage).__name__
    if "problem_id" not in table.columns:
        raise ValueError(f"{stage_name} outputs a table without a problem_id column.")
    if table["problem_id"].is_duplicated().any():
        raise ValueError(f"{stage_name} outputs a table that holds a problem_id more than once.")
    dropped_columns = [column for column in previous_table.columns if column not in table.columns]
    if dropped_columns:
        raise ValueError(f"{stage_name} drops the columns {dropped_columns} of the table before it.")
    if "problem_id" in previous_table.columns:
        added_problem_ids = set(table["problem_id"].to_list()) - set(previous_table["problem_id"].to_list())
        if added_problem_ids:
            raise ValueError(
                f"{stage_name} outputs rows that the table before it does not hold: {sorted(added_problem_ids)}."
            )
