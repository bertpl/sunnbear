"""`run_pipeline` runs the stages of the benchmark suite pipeline in order on a set of formulas."""

from collections.abc import Sequence
from pathlib import Path

from sunnbear._core.functions.core import Formula
from sunnbear._core.utils.module_imports import worker_pool_for_modules

from .core import PipelineStageManifest, PipelineWorkspace, run_stages
from .stages import CandidateGenerationStage, CandidateValidationStage


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(
    *, workspace_dir: Path, formulas: Sequence[Formula], n_workers: int | None = None
) -> tuple[PipelineStageManifest, ...]:
    """Run every stage of the benchmark suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its output and manifest replace those of an earlier run. The stages share 1
    `WorkerPool`, whose workers start only when a stage first runs tasks in it.

    Args:
        workspace_dir: The directory for the outputs of the stages.
        formulas: The formulas whose candidates the pipeline builds.
        n_workers: The number of worker processes; ``None`` for 1 per CPU. Each worker imports the modules that
            define `formulas`, so with more than 1 worker, no formula may be defined in an interactive session.

    Returns:
        The manifest of each stage, in run order.

    Raises:
        ValueError: If a formula fails the checks of `Formula.build_all_candidates`, or if `n_workers` is below 1, or
            above 1 while a formula is defined in an interactive session.
    """
    stages = [CandidateGenerationStage(formulas), CandidateValidationStage()]
    module_names = {type(formula).__module__ for formula in formulas}
    with worker_pool_for_modules(n_workers=n_workers, module_names=module_names) as worker_pool:
        return run_stages(PipelineWorkspace(workspace_dir), stages, worker_pool=worker_pool)
