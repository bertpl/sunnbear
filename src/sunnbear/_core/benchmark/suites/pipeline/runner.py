"""`run_pipeline` runs the stages of the benchmark suite pipeline in order on a set of formulas."""

from collections.abc import Sequence
from pathlib import Path

from sunnbear._core.problems.core import Formula
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.utils.module_imports import worker_pool_for_modules

from .core import PipelineRunResult, PipelineWorkspace, run_stages
from .mode import PipelineMode
from .stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    CoreSelectionStage,
    FullCharacterizationStage,
    SpacingStage,
)


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(
    *,
    workspace_dir: Path,
    formulas: Sequence[Formula],
    core_solver_configs: Sequence[SolverConfig],
    n_workers: int | None = None,
    mode: PipelineMode = PipelineMode.FULL,
) -> PipelineRunResult:
    """Run every stage of the benchmark suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its output and manifest replace those of an earlier run. The stages share 1
    `WorkerPool`, whose workers start only when a stage first runs tasks in it.

    Args:
        workspace_dir: The directory for the outputs of the stages.
        formulas: The formulas whose candidates the pipeline builds.
        core_solver_configs: The solver configs whose solves characterize the candidates: for the benchmark suites,
            the configs whose role marks them for characterizing test problems
            (`SolverRole.is_used_for_problem_characterization`).
        n_workers: The number of worker processes; ``None`` for 1 per logical CPU. Each worker imports the modules that
            define `formulas` and `core_solver_configs`, so with more than 1 worker, none of them may be defined in an
            interactive session.
        mode: How much work the stages do, as `PipelineMode` describes it; full characterization and core selection
            are built from its attributes.

    Returns:
        The manifest of each stage that wrote its output, in run order, and the stage that stopped the run, if any, as
        `run_stages` describes it.

    Raises:
        ValueError: If 1 of these holds:

            - a formula fails the checks of `Formula.build_all_candidates`;
            - `core_solver_configs` is empty;
            - `n_workers` is below 1, or above 1 while a formula or solver config is defined in an interactive session.
    """
    stages = [
        CandidateGenerationStage(formulas),
        CandidateValidationStage(),
        CoarseCharacterizationStage(core_solver_configs),
        SpacingStage(),
        FullCharacterizationStage(core_solver_configs, fidelity=mode.full_characterization_fidelity),
        CoreSelectionStage(sec_per_candidate=mode.core_selection_sec_per_candidate),
    ]
    module_names = {type(formula).__module__ for formula in formulas} | {
        config.declaring_module_name for config in core_solver_configs
    }
    with worker_pool_for_modules(n_workers=n_workers, module_names=module_names) as worker_pool:
        return run_stages(PipelineWorkspace(workspace_dir), stages, worker_pool=worker_pool)
