"""`run_pipeline` runs the stages of the suite pipeline in order, and writes each stage's output and manifest."""

import datetime
import time
from collections.abc import Callable, Sequence
from pathlib import Path

import polars as pl

from sunnbear._core.functions.core import Formula

from .generation import generate_candidates
from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .validation import validate_candidates
from .workspace import PipelineWorkspace


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(*, workspace_dir: Path, formulas: Sequence[Formula]) -> tuple[PipelineStageManifest, ...]:
    """Run every stage of the suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its output and manifest replace those of an earlier run.

    Returns:
        The manifest of each stage, in run order.

    Raises:
        ValueError: If a formula fails the checks of `Formula.build_all_candidates`.
    """
    workspace = PipelineWorkspace(workspace_dir)
    candidates, generation_manifest = _run_stage(
        workspace, PipelineStage.CANDIDATE_GENERATION, (), lambda: generate_candidates(formulas)
    )
    _, validation_manifest = _run_stage(
        workspace, PipelineStage.CANDIDATE_VALIDATION, (generation_manifest,), lambda: validate_candidates(candidates)
    )
    return (generation_manifest, validation_manifest)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _run_stage(
    workspace: PipelineWorkspace,
    stage: PipelineStage,
    input_manifests: Sequence[PipelineStageManifest],
    compute_output: Callable[[], pl.DataFrame],
) -> tuple[pl.DataFrame, PipelineStageManifest]:
    """Compute the output of `stage`, write it and its manifest into `workspace`, and return both.

    `input_manifests` are the manifests of the stages whose outputs `compute_output` reads.
    """
    started_at = datetime.datetime.now(datetime.UTC)
    t_start = time.perf_counter()
    output = compute_output()
    duration_sec = time.perf_counter() - t_start
    manifest = workspace.write_stage(
        stage=stage, output=output, input_manifests=input_manifests, started_at=started_at, duration_sec=duration_sec
    )
    return output, manifest
