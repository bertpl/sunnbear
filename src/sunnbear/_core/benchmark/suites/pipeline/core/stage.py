"""`PipelineStage` is the base class of a stage of the benchmark suite pipeline."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import ClassVar

from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool, WorkerTask

from .stage_id import PipelineStageId

# A stage's parameter value is a JSON scalar, so that its manifest can record it.
type PipelineStageParameterValue = bool | int | float | str

# The largest number of candidates in 1 task of `PipelineStage._run_in_formula_batches`. Splitting a large formula
# over several tasks shortens a stage, because:
# - a stage cannot end before its longest task does;
# - the time per candidate differs widely between candidates, and the neighbors of a slow candidate in a formula's
#   order are usually slow too;
# - compiling a formula takes far less time than running 1 slow candidate, so splitting a formula over several workers
#   costs little.
MAX_CANDIDATES_PER_TASK = 50


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage[StateAccessorT](ABC):
    """A `PipelineStage` reads what earlier stages found about the candidates, and adds its own information.

    The run passes each stage the state accessor of the stage's `stage_id`, which is all that the stage sees of the
    run's `PipelineState`:

    - the candidates that no stage has dropped;
    - the information of earlier stages that the stage needs;
    - the methods that write the stage's own information and record its drops.

    `StateAccessorT` is the class of that accessor.

    Class attributes:
        stage_id: The stage's `PipelineStageId`, which sets its place in the run order and its state accessor.
    """

    stage_id: ClassVar[PipelineStageId]

    @property
    def parameters(self) -> Mapping[str, PipelineStageParameterValue]:
        """Return the values of the stage's parameters, keyed by name, for its `PipelineStageManifest` to record.

        A stage whose results depend on a value given to its constructor, such as a threshold, returns it here; the
        base implementation returns no parameter.
        """
        return {}

    @abstractmethod
    def run(self, state_accessor: StateAccessorT, *, worker_pool: WorkerPool) -> None:
        """Run the stage on `state_accessor`: read its candidates, and record the stage's information and its drops.

        Args:
            state_accessor: The stage's state accessor.
            worker_pool: The worker pool of the run, in which the stage may run tasks. The stage's results must not
                depend on the pool's number of workers. The stage's tasks must be picklable `WorkerTask`s. A worker has
                imported the modules that define the run's formulas, and otherwise only what unpickling a task needs.
        """

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _run_in_formula_batches[C, R](
        candidates: Sequence[C],
        *,
        problem_id_key: Callable[[C], ProblemId],
        build_task: Callable[[tuple[C, ...]], WorkerTask[list[R]]],
        worker_pool: WorkerPool,
    ) -> dict[ProblemId, R]:
        """Return each candidate's result from `build_task`, keyed by problem id, from batches grouped by formula.

        The candidates of a formula go to the same task when they fit within a batch's maximum size, which
        `WorkerPool.split_into_batches` sets and `MAX_CANDIDATES_PER_TASK` caps, so most formulas are compiled in only
        1 worker. A larger formula is split over several tasks, so that its candidates run in several workers.

        Args:
            candidates: The candidates to run, each with a distinct problem id.
            problem_id_key: Returns a candidate's problem id.
            build_task: Builds the task of 1 batch, whose `run` returns 1 result per candidate of the batch, in the
                batch's order.
            worker_pool: The worker pool of the run, which splits the candidates into batches and runs their tasks.
        """
        batches = worker_pool.split_into_batches(
            candidates,
            group_key=lambda candidate: problem_id_key(candidate).formula_id,
            max_batch_size=MAX_CANDIDATES_PER_TASK,
        )
        tasks = {batch_idx: build_task(tuple(batch)) for batch_idx, batch in enumerate(batches)}
        results_by_problem_id: dict[ProblemId, R] = {}
        for batch_idx, results in worker_pool.run(tasks):
            results_by_problem_id.update(zip(map(problem_id_key, batches[batch_idx]), results, strict=True))
        return results_by_problem_id
