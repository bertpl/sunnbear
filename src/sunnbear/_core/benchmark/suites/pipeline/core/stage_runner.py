"""`run_stages` runs stages of the benchmark suite pipeline in order, and writes each stage's output and manifest."""

import datetime
import time
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .workspace import PipelineWorkspace

if TYPE_CHECKING:  # type-only: polars appears here only in the annotation of a local variable
    import polars as pl


# ==================================================================================================
#  run_stages
# ==================================================================================================
def run_stages(workspace: PipelineWorkspace, stages: Sequence[PipelineStage]) -> tuple[PipelineStageManifest, ...]:
    """Run `stages` in order, and have `workspace` write each stage's output and manifest.

    Each stage receives the outputs of its `PipelineStage.input_stages`, which must run before it.

    Returns:
        The manifest of each stage, in run order.

    Raises:
        ValueError: If a stage reads the output of a stage that does not run before it.
    """
    outputs: dict[type[PipelineStage], pl.DataFrame] = {}
    manifests: dict[type[PipelineStage], PipelineStageManifest] = {}
    for stage in stages:
        # --- inputs -----------------------------
        missing_stage_names = [input_stage.__name__ for input_stage in stage.input_stages if input_stage not in outputs]
        if missing_stage_names:
            raise ValueError(
                f"{type(stage).__name__} reads the outputs of {missing_stage_names}, which do not run before it."
            )
        inputs = {input_stage: outputs[input_stage] for input_stage in stage.input_stages}

        # --- output -----------------------------
        started_at = datetime.datetime.now(datetime.UTC)
        t_start = time.perf_counter()
        output = stage.compute_output(inputs)
        duration_sec = time.perf_counter() - t_start

        # --- output and manifest files ----------
        manifests[type(stage)] = workspace.write_stage(
            stage=stage,
            output=output,
            input_manifests=[manifests[input_stage] for input_stage in stage.input_stages],
            started_at=started_at,
            duration_sec=duration_sec,
        )
        outputs[type(stage)] = output
    return tuple(manifests.values())
