"""`run_stages` runs the stages of the benchmark suite pipeline as a chain, and writes their outputs and manifests."""

import datetime
import time
from collections.abc import Sequence

import polars as pl

from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .workspace import PipelineWorkspace


# ==================================================================================================
#  run_stages
# ==================================================================================================
def run_stages(workspace: PipelineWorkspace, stages: Sequence[PipelineStage]) -> tuple[PipelineStageManifest, ...]:
    """Run `stages` in order, each on the output of the stage before it, and have `workspace` write each output.

    The first stage receives an empty table.

    Returns:
        The manifest of each stage, in run order.

    Raises:
        ValueError: If a stage's output lacks a column of the output before it.
    """
    previous_output = pl.DataFrame()
    previous_manifest: PipelineStageManifest | None = None
    manifests: list[PipelineStageManifest] = []
    for stage in stages:
        # --- output -----------------------------
        started_at = datetime.datetime.now(datetime.UTC)
        t_start = time.perf_counter()
        output = stage.compute_output(previous_output)
        duration_sec = time.perf_counter() - t_start

        # --- the chain's rule -------------------
        dropped_columns = [column for column in previous_output.columns if column not in output.columns]
        if dropped_columns:
            raise ValueError(f"{type(stage).__name__} drops the columns {dropped_columns} of the output before it.")

        # --- output and manifest files ----------
        manifest = workspace.write_stage_output_and_manifest(
            stage=stage,
            output=output,
            input_manifest=previous_manifest,
            started_at=started_at,
            duration_sec=duration_sec,
        )
        manifests.append(manifest)
        previous_output, previous_manifest = output, manifest
    return tuple(manifests)
