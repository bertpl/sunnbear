"""`run_pipeline` runs the stages of the suite pipeline in order, and writes each stage's output and manifest."""

import datetime
import importlib.metadata
import time
from collections.abc import Callable, Sequence
from pathlib import Path

import polars as pl

from sunnbear._core.functions.core import Formula

from .generation import generate_candidates
from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .validation import count_rejections, validate_candidates
from .workspace import PipelineWorkspace


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(*, workspace_dir: Path, formulas: Sequence[Formula]) -> tuple[PipelineStageManifest, ...]:
    """Run every stage of the suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its output and manifest replace those of an earlier run.

    Returns:
        The manifest of each stage, in run order.
    """
    workspace = PipelineWorkspace(workspace_dir)
    candidates, candidates_manifest = _run_stage(
        workspace, PipelineStage.CANDIDATE_GENERATION, (), lambda: generate_candidates(formulas)
    )
    _, validation_manifest = _run_stage(
        workspace, PipelineStage.VALIDATION, (candidates_manifest,), lambda: validate_candidates(candidates)
    )
    return (candidates_manifest, validation_manifest)


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

    Args:
        workspace: The workspace to write into.
        stage: The stage to run.
        input_manifests: The manifests of the stages whose outputs `compute_output` reads.
        compute_output: Computes the stage's output.
    """
    started_at = datetime.datetime.now(datetime.UTC)
    t_start = time.perf_counter()
    output = compute_output()
    duration_sec = time.perf_counter() - t_start
    manifest = PipelineStageManifest(
        stage=stage,
        output_sha256=workspace.write_stage_output(stage, output),
        input_sha256s={input_manifest.stage: input_manifest.output_sha256 for input_manifest in input_manifests},
        sunnbear_version=importlib.metadata.version("sunnbear"),
        n_rows=output.height,
        rejection_counts=count_rejections(output),
        started_at=started_at,
        duration_sec=duration_sec,
    )
    workspace.write_manifest(manifest)
    return output, manifest
