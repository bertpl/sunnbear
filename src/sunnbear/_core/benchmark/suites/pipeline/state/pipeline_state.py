"""`PipelineState` holds what a run of the benchmark suite pipeline knows about its candidates."""

from typing import Any

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageId
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

from .accessors import (
    CandidateGenerationStateAccessor,
    CandidateValidationStateAccessor,
    CoarseCharacterizationStateAccessor,
    CoreSelectionStateAccessor,
    DistillationStateAccessor,
    FullCharacterizationStateAccessor,
    PipelineStateAccessor,
    SpacingStateAccessor,
)
from .candidate_registry import CandidateDrop
from .storage import PipelineStateStorage

_ACCESSOR_CLASSES: dict[PipelineStageId, type[PipelineStateAccessor]] = {
    accessor_cls.stage_id: accessor_cls
    for accessor_cls in (
        CandidateGenerationStateAccessor,
        CandidateValidationStateAccessor,
        CoarseCharacterizationStateAccessor,
        SpacingStateAccessor,
        FullCharacterizationStateAccessor,
        CoreSelectionStateAccessor,
        DistillationStateAccessor,
    )
}


# ==================================================================================================
#  PipelineState
# ==================================================================================================
class PipelineState:
    """A `PipelineState` holds every candidate of a run, and each stage's information on the candidates.

    The state is mutable, and a run keeps 1 for all its stages. Each stage reaches the state only through the state
    accessor that `create_state_accessor` makes for it.

    The stages run in the order of `PipelineStageId`, so the state makes a stage's accessor only once every earlier
    stage has finished, and the stage then finds the information of every earlier stage.

    A candidate that a stage drops keeps its entry in the state, with the stage, the reason, and whether the stage
    rejected it as invalid; the later stages no longer see the candidate.
    """

    def __init__(self) -> None:
        """Create the state of a run that has no candidates yet."""
        self._storage = PipelineStateStorage()
        self._started_stage_ids: list[PipelineStageId] = []
        self._finished_stage_ids: list[PipelineStageId] = []

    @property
    def n_remaining_candidates(self) -> int:
        """Return the number of candidates that no stage has dropped."""
        return len(self._storage.candidate_registry.remaining_problem_ids)

    @property
    def finished_stage_ids(self) -> tuple[PipelineStageId, ...]:
        """Return the stages that have finished, in run order."""
        return tuple(self._finished_stage_ids)

    def drop_of(self, problem_id: ProblemId) -> CandidateDrop | None:
        """Return the drop of the candidate `problem_id`, or ``None`` if no stage has dropped it.

        Raises:
            KeyError: If `problem_id` is not a candidate of the run.
        """
        return self._storage.candidate_registry.drop_of(problem_id)

    def create_state_accessor(self, stage_id: PipelineStageId) -> PipelineStateAccessor:
        """Return the state accessor of the stage `stage_id`, which the stage then runs on.

        Raises:
            ValueError: If `stage_id` is not the next stage in run order: a stage before it has not finished, or the
                stage has an accessor already.
        """
        next_stage_id = list(PipelineStageId)[len(self._finished_stage_ids)]
        if stage_id != next_stage_id or stage_id in self._started_stage_ids:
            raise ValueError(f"The state creates no accessor for {stage_id}: the next stage to run is {next_stage_id}.")
        else:
            self._started_stage_ids.append(stage_id)
            return _ACCESSOR_CLASSES[stage_id](self._storage)

    def finish_stage(self, stage_id: PipelineStageId) -> None:
        """Record that the stage `stage_id` has run to its end, so that the next stage can start.

        Raises:
            ValueError: If the stage has no accessor yet, or has finished already.
        """
        if stage_id not in self._started_stage_ids or stage_id in self._finished_stage_ids:
            raise ValueError(f"{stage_id} has not started, or has finished already.")
        else:
            self._finished_stage_ids.append(stage_id)

    def run_stage(self, stage: PipelineStage[Any], *, worker_pool: WorkerPool) -> None:
        """Run `stage` on the state accessor that the state creates for it, then record that the stage has finished.

        A stage that raises, for example `PipelineStopError`, does not finish, and the error propagates.

        Raises:
            ValueError: If `stage` is not the next stage in run order.
        """
        stage.run(self.create_state_accessor(stage.stage_id), worker_pool=worker_pool)
        self.finish_stage(stage.stage_id)
