"""`run_pipeline` runs the stages of the benchmark suite pipeline in order on a set of formulas."""

from collections.abc import Sequence
from pathlib import Path

from sunnbear._core.functions.core import Formula

from .core import PipelineStageManifest, PipelineWorkspace, run_stages
from .stages import CandidateGeneration, CandidateValidation


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(*, workspace_dir: Path, formulas: Sequence[Formula]) -> tuple[PipelineStageManifest, ...]:
    """Run every stage of the benchmark suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its output and manifest replace those of an earlier run.

    Returns:
        The manifest of each stage, in run order.

    Raises:
        ValueError: If a formula fails the checks of `Formula.build_all_candidates`.
    """
    stages = [CandidateGeneration(formulas), CandidateValidation()]
    return run_stages(PipelineWorkspace(workspace_dir), stages)
