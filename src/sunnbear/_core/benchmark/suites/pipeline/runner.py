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
from .diversity_features import DiversityFeatureFactory
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
from .state import BenchmarkSuitesBuildDetails, PipelineState


# ==================================================================================================
#  run_pipeline
# ==================================================================================================
def run_pipeline(
    *,
    workspace_dir: Path,
    formulas: Sequence[Formula],
    n_workers: int | None = None,
    mode: PipelineMode = PipelineMode.FULL,
) -> "PipelineRunResult":
    """Run every stage of the benchmark suite pipeline on `formulas`, into the workspace directory `workspace_dir`.

    Every stage is recomputed, and its manifest replaces that of an earlier run. The stages share 1 `WorkerPool`, whose
    workers start only when a stage first runs tasks in it.

    Args:
        workspace_dir: The directory for the manifests of the stages and the build details of the run.
        formulas: The formulas whose candidates the pipeline builds.
        n_workers: The number of worker processes; ``None`` for 1 per logical CPU. Each worker imports the modules that
            define `formulas` and `DiversityFeatureFactory.solver_configs`, so with more than 1 worker, no formula may
            be defined in an interactive session.
        mode: The `PipelineMode`, whose attributes set how much work the stages do.

    Returns:
        The run's result, as `run_stages` describes it.

    Raises:
        ValueError: If 1 of these holds:

            - a formula fails the checks of `Formula.build_all_candidates`;
            - `n_workers` is below 1, or above 1 while a formula is defined in an interactive session.
    """
    stages = [
        CandidateGenerationStage(formulas),
        CandidateValidationStage(),
        CoarseCharacterizationStage(fidelity=mode.coarse_characterization_stage_fidelity),
        SpacingStage(),
        FullCharacterizationStage(fidelity=mode.full_characterization_stage_fidelity),
        CoreSelectionStage(sec_per_candidate=mode.selection_sec_per_candidate),
        DistillationStage(sec_per_candidate=mode.selection_sec_per_candidate),
    ]
    module_names = {type(formula).__module__ for formula in formulas} | {
        config.declaring_module_name for config in DiversityFeatureFactory().solver_configs
    }
    with worker_pool_for_modules(n_workers=n_workers, module_names=module_names) as worker_pool:
        return run_stages(PipelineWorkspace(workspace_dir), stages, worker_pool=worker_pool)


# ==================================================================================================
#  run_stages
# ==================================================================================================
def run_stages(
    workspace: PipelineWorkspace, stages: Sequence[PipelineStage[Any]], *, worker_pool: WorkerPool
) -> "PipelineRunResult":
    """Run `stages` in order on 1 new `PipelineState`; write each stage's manifest and the build details to `workspace`.

    Each stage runs on the state accessor that the state creates for it, so `stages` must follow the run order of
    `PipelineStageId`, starting at its first member; the list may stop before its last member.

    Every stage receives `worker_pool`, in which it may run tasks, and its manifest records the pool's number of
    workers. A `worker_pool` with more than 1 worker must be inside its ``with`` block, which `run_stages` does not
    open.

    A stage that raises `PipelineStopError` stops the run: it writes no manifest, and the stages after it do not run.
    Whether a stage stops the run or not, the run then creates its build details and writes their files to `workspace`.

    Raises:
        ValueError: If `stages` do not follow the run order of `PipelineStageId`.
    """
    state = PipelineState()
    manifests: list[PipelineStageManifest] = []
    stop: PipelineStop | None = None
    for stage in stages:
        n_candidates_in = state.n_remaining_candidates
        started_at = datetime.datetime.now(datetime.UTC)
        t_start = time.perf_counter()
        try:
            state.run_stage(stage, worker_pool=worker_pool)
        except PipelineStopError as error:
            stop = PipelineStop(stage_id=stage.stage_id, reason=str(error))
            break
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
    build_details = state.create_build_details(stop=stop)
    workspace.write_build_details_files(build_details.to_files())
    return PipelineRunResult(manifests=tuple(manifests), build_details=build_details)


# ==================================================================================================
#  PipelineRunResult
# ==================================================================================================
@dataclass(frozen=True)
class PipelineRunResult:
    """A `PipelineRunResult` holds the manifests of a run's stages, and the run's build details.

    Attributes:
        manifests: The manifest of each stage that ran to its end, in run order.
        build_details: The run's `BenchmarkSuitesBuildDetails`, which hold the stage that stopped the run, if any.
    """

    manifests: tuple[PipelineStageManifest, ...]
    build_details: BenchmarkSuitesBuildDetails
