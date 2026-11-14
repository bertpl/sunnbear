"""`PipelineStage._run_in_formula_batches` runs the candidates in tasks grouped by formula, and limits each task's
number of candidates."""

from dataclasses import dataclass

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.benchmark.suites.pipeline.core.stage import MAX_CANDIDATES_PER_TASK
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool


@dataclass(frozen=True)
class _ExampleProblemIdTextTask:
    """`_ExampleProblemIdTextTask` returns the text of each of its problem ids."""

    problem_ids: tuple[ProblemId, ...]

    def run(self) -> list[str]:
        """Return each problem id as text, in order."""
        return list(map(str, self.problem_ids))


def test_a_formula_with_many_candidates_is_split_over_tasks_of_limited_size():
    """`_run_in_formula_batches` runs the candidates as follows:

    - a formula with 5 times `MAX_CANDIDATES_PER_TASK` candidates runs in several tasks, none above that maximum;
    - a small formula runs in 1 task;
    - every candidate gets its own result.
    """
    # --- arrange ----------------------
    large_formula_problem_ids = [ProblemId.from_string(f"f99.901[n={n}.0]") for n in range(5 * MAX_CANDIDATES_PER_TASK)]
    small_formula_problem_ids = [ProblemId.from_string(f"f99.902[n={n}.0]") for n in range(3)]
    tasks: list[_ExampleProblemIdTextTask] = []

    def build_task(batch: tuple[ProblemId, ...]) -> _ExampleProblemIdTextTask:
        """Build the task for `batch` and record it in `tasks`."""
        tasks.append(_ExampleProblemIdTextTask(problem_ids=batch))
        return tasks[-1]

    # --- act --------------------------
    results = PipelineStage._run_in_formula_batches(
        large_formula_problem_ids + small_formula_problem_ids,
        problem_id_key=lambda problem_id: problem_id,
        build_task=build_task,
        worker_pool=WorkerPool(n_workers=1),
    )

    # --- assert -----------------------
    assert results == {
        problem_id: str(problem_id) for problem_id in large_formula_problem_ids + small_formula_problem_ids
    }
    assert max(len(task.problem_ids) for task in tasks) == MAX_CANDIDATES_PER_TASK
    tasks_of_small_formula = [task for task in tasks if small_formula_problem_ids[0] in task.problem_ids]
    assert [task.problem_ids for task in tasks_of_small_formula] == [tuple(small_formula_problem_ids)]
