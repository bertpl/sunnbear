"""`run_pipeline` runs the stages of the benchmark suite pipeline in order on a set of formulas.

`run_stages` runs a list of stages on 1 `PipelineState`, which `run_pipeline` builds from every stage of the package
`stages`.
"""

import datetime
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sunnbear._core.problems.core import Formula
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.utils.module_imports import worker_pool_for_modules
from sunnbear._core.utils.worker_pool import WorkerPool

from .core import (
    PipelineStage,
    PipelineStageExecutionInfo,
    PipelineStageManifest,
    PipelineStop,
    PipelineStopError,
    PipelineWorkspace,
)
from .mode import PipelineMode
from .stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    CoreSelectionStage,
    DistillationStage,
    FullCharacterizationStage,
    SpacingStage,
)
from .state import PipelineState


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
) -> "PipelineRunResult":
    """Run every stage of the benchmark suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its manifest replaces that of an earlier run. The stages share 1 `WorkerPool`, whose
    workers start only when a stage first runs tasks in it.

    Args:
        workspace_dir: The directory for the manifests of the stages.
        formulas: The formulas whose candidates the pipeline builds.
        core_solver_configs: The solver configs whose solves characterize the candidates: for the benchmark suites,
            the configs whose role marks them for characterizing test problems
            (`SolverRole.is_used_for_problem_characterization`).
        n_workers: The number of worker processes; ``None`` for 1 per logical CPU. Each worker imports the modules that
            define `formulas` and `core_solver_configs`, so with more than 1 worker, none of them may be defined in an
            interactive session.
        mode: The `PipelineMode`, whose attributes set how much work the stages do.

    Returns:
        The run's result, as `run_stages` describes it.

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
        FullCharacterizationStage(core_solver_configs, fidelity=mode.full_characterization_stage_fidelity),
        CoreSelectionStage(sec_per_candidate=mode.selection_sec_per_candidate),
        DistillationStage(sec_per_candidate=mode.selection_sec_per_candidate),
    ]
    module_names = {type(formula).__module__ for formula in formulas} | {
        config.declaring_module_name for config in core_solver_configs
    }
    with worker_pool_for_modules(n_workers=n_workers, module_names=module_names) as worker_pool:
        return run_stages(PipelineWorkspace(workspace_dir), stages, worker_pool=worker_pool)


# ==================================================================================================
#  run_stages
# ==================================================================================================
def run_stages(
    workspace: PipelineWorkspace, stages: Sequence[PipelineStage[Any]], *, worker_pool: WorkerPool
) -> "PipelineRunResult":
    """Run `stages` in order on 1 new `PipelineState`, and have `workspace` write each stage's manifest.

    Each stage runs on the state accessor that the state creates for it, so `stages` must follow the run order of
    `PipelineStageId`, starting at its first member; the list may stop before its last member.

    Every stage receives `worker_pool`, in which it may run tasks, and its manifest records the pool's number of
    workers. A `worker_pool` with more than 1 worker must be inside its ``with`` block, which `run_stages` does not
    open.

    A stage that raises `PipelineStopError` stops the run: it writes no manifest, and the stages after it do not run.

    Returns:
        The run's `PipelineRunResult`, which holds:

        - the manifest of each stage that ran to its end, in run order;
        - the `PipelineStop` of the stage that stopped the run, if any;
        - the run's state.

    Raises:
        ValueError: If `stages` do not follow the run order of `PipelineStageId`.
    """
    state = PipelineState()
    manifests: list[PipelineStageManifest] = []
    for stage in stages:
        n_candidates_in = state.n_remaining_candidates
        started_at = datetime.datetime.now(datetime.UTC)
        t_start = time.perf_counter()
        try:
            state.run_stage(stage, worker_pool=worker_pool)
        except PipelineStopError as error:
            return PipelineRunResult(
                manifests=tuple(manifests), stop=PipelineStop(stage_id=stage.stage_id, reason=str(error)), state=state
            )
        duration_sec = time.perf_counter() - t_start
        manifest = PipelineStageManifest.from_stage_run(
            stage=stage,
            n_candidates_in=n_candidates_in,
            n_candidates_out=state.n_remaining_candidates,
            execution_info=PipelineStageExecutionInfo(
                started_at=started_at, duration_sec=duration_sec, n_workers=worker_pool.n_workers
            ),
        )
        workspace.write_manifest(manifest)
        manifests.append(manifest)
    return PipelineRunResult(manifests=tuple(manifests), stop=None, state=state)


# ==================================================================================================
#  PipelineRunResult
# ==================================================================================================
@dataclass(frozen=True)
class PipelineRunResult:
    """A `PipelineRunResult` holds the manifests of a run's stages, the stop that ended the run early, and its state.

    Attributes:
        manifests: The manifest of each stage that ran to its end, in run order.
        stop: The stage that stopped the run, and why; ``None`` when every stage ran to its end.
        state: The run's `PipelineState`, with the information of every stage that ran.
    """

    manifests: tuple[PipelineStageManifest, ...]
    stop: PipelineStop | None
    state: PipelineState
