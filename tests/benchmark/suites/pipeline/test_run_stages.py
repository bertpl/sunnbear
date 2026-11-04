"""The tests of `run_stages` check that:

- the stages run in order on 1 state, and each stage's manifest is written into the workspace and counts its
  candidates;
- a rerun replaces the manifests and leaves no temporary files;
- stages out of run order are refused;
- a stage that raises `PipelineStopError` ends the run, which returns the stop with the earlier stages' manifests;
- a stage that runs tasks in the worker pool gives the same information with 1 or 2 workers.
"""

from dataclasses import dataclass

import pytest

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import (
    PipelineStage,
    PipelineStageId,
    PipelineStageManifest,
    PipelineStop,
    PipelineStopError,
    PipelineWorkspace,
)
from sunnbear._core.benchmark.suites.pipeline.runner import run_stages
from sunnbear._core.benchmark.suites.pipeline.state import (
    CandidateGenerationStateAccessor,
    CandidateValidationStateAccessor,
    CoarseCharacterizationStateAccessor,
    IntervalBounds,
)
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

# A pool with 1 worker runs its tasks in this process and needs no with block.
_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)
_PROBLEM_IDS = example_problem_ids(3)


class _ExampleGenerationStage(PipelineStage[CandidateGenerationStateAccessor]):
    """`_ExampleGenerationStage` adds 3 example candidates."""

    stage_id = PipelineStageId.CANDIDATE_GENERATION

    def run(self, state_accessor: CandidateGenerationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Add the candidates, each on ``[-1, 1]``."""
        state_accessor.add_candidates(dict.fromkeys(_PROBLEM_IDS, IntervalBounds(a=-1.0, b=1.0)))


@dataclass(frozen=True)
class _ExampleCRangeTask:
    """`_ExampleCRangeTask` computes the c-range ``[-n, n]`` of each candidate's position ``n``, in a worker."""

    positions: tuple[int, ...]

    def run(self) -> list[CRange]:
        """Return each position's c-range, in order."""
        return [CRange(c_min=-float(position), c_max=float(position)) for position in self.positions]


class _ExampleValidationStage(PipelineStage[CandidateValidationStateAccessor]):
    """`_ExampleValidationStage` rejects the first candidate, and stores a c-range from tasks for the others."""

    stage_id = PipelineStageId.CANDIDATE_VALIDATION

    @property
    def parameters(self) -> dict[str, int]:
        """Return an example parameter."""
        return {"n_rejected": 1}

    def run(self, state_accessor: CandidateValidationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Reject the first candidate; compute the c-range of the n-th candidate in a task, as ``[-n, n]``."""
        [rejected_problem_id, *kept_problem_ids] = state_accessor.remaining_problem_ids
        state_accessor.reject(rejected_problem_id, "example_reason")
        batches = worker_pool.split_into_batches(list(range(1, len(kept_problem_ids) + 1)), group_key=lambda n: n)
        tasks = {batch_idx: _ExampleCRangeTask(positions=tuple(batch)) for batch_idx, batch in enumerate(batches)}
        c_range_by_position = {}
        for batch_idx, c_ranges in worker_pool.run(tasks):
            c_range_by_position.update(zip(batches[batch_idx], c_ranges, strict=True))
        state_accessor.set_c_ranges(
            {problem_id: c_range_by_position[idx + 1] for idx, problem_id in enumerate(kept_problem_ids)}
        )


class _ExampleStoppingStage(PipelineStage[CoarseCharacterizationStateAccessor]):
    """`_ExampleStoppingStage` stops the run, as a stage does when its candidates cannot give a valid result."""

    stage_id = PipelineStageId.COARSE_CHARACTERIZATION

    def run(self, state_accessor: CoarseCharacterizationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Raise `PipelineStopError`, which names the number of candidates."""
        raise PipelineStopError(f"{len(state_accessor.remaining_problem_ids)} candidates are too few.")


def test_the_stages_run_in_order_and_their_manifests_are_written(tmp_path):
    """Each manifest file holds its stage's manifest, which counts the candidates at the stage's start and end and
    records its parameters; the next stage's accessor finds the stages' information."""
    # --- act --------------------------
    result = run_stages(
        PipelineWorkspace(tmp_path),
        [_ExampleGenerationStage(), _ExampleValidationStage()],
        worker_pool=_IN_PROCESS_WORKER_POOL,
    )

    # --- assert -----------------------
    assert result.stop is None
    for manifest in result.manifests:
        manifest_file = tmp_path / "manifests" / f"{manifest.stage_id}.json"
        assert PipelineStageManifest.model_validate_json(manifest_file.read_text()) == manifest
    generation_manifest, validation_manifest = result.manifests
    assert (generation_manifest.n_candidates_in, generation_manifest.n_candidates_out) == (0, 3)
    assert (validation_manifest.n_candidates_in, validation_manifest.n_candidates_out) == (3, 2)
    assert (generation_manifest.parameters, validation_manifest.parameters) == ({}, {"n_rejected": 1})
    assert result.state.create_state_accessor(PipelineStageId.COARSE_CHARACTERIZATION).c_ranges() == {
        _PROBLEM_IDS[1]: CRange(c_min=-1.0, c_max=1.0),
        _PROBLEM_IDS[2]: CRange(c_min=-2.0, c_max=2.0),
    }


def test_a_rerun_replaces_the_manifests_and_leaves_no_temporary_files(tmp_path):
    """A second run into the same workspace replaces every manifest of the first, and leaves only the final files."""
    # --- arrange ----------------------
    workspace = PipelineWorkspace(tmp_path)
    run_stages(workspace, [_ExampleGenerationStage(), _ExampleValidationStage()], worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- act --------------------------
    second_manifests = run_stages(
        workspace, [_ExampleGenerationStage(), _ExampleValidationStage()], worker_pool=_IN_PROCESS_WORKER_POOL
    ).manifests

    # --- assert -----------------------
    stage_ids = [PipelineStageId.CANDIDATE_GENERATION, PipelineStageId.CANDIDATE_VALIDATION]
    assert [
        PipelineStageManifest.model_validate_json((tmp_path / "manifests" / f"{stage_id}.json").read_text())
        for stage_id in stage_ids
    ] == list(second_manifests)
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.*")) == [
        f"manifests/{stage_id}.json" for stage_id in stage_ids
    ]


def test_stages_out_of_run_order_are_refused(tmp_path):
    """A run that starts with validation, before candidate generation, is refused."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="the next stage to run is s1_candidate_generation"):
        run_stages(PipelineWorkspace(tmp_path), [_ExampleValidationStage()], worker_pool=_IN_PROCESS_WORKER_POOL)


def test_a_stage_that_raises_a_pipeline_stop_error_ends_the_run(tmp_path):
    """The stopping stage writes no manifest; the result holds the earlier stages' manifests and the stop, with the
    stopping stage's id and the error's message."""
    # --- act --------------------------
    result = run_stages(
        PipelineWorkspace(tmp_path),
        [_ExampleGenerationStage(), _ExampleValidationStage(), _ExampleStoppingStage()],
        worker_pool=_IN_PROCESS_WORKER_POOL,
    )

    # --- assert -----------------------
    assert [manifest.stage_id for manifest in result.manifests] == [
        PipelineStageId.CANDIDATE_GENERATION,
        PipelineStageId.CANDIDATE_VALIDATION,
    ]
    assert result.stop == PipelineStop(
        stage_id=PipelineStageId.COARSE_CHARACTERIZATION, reason="2 candidates are too few."
    )
    assert result.state.finished_stage_ids == (
        PipelineStageId.CANDIDATE_GENERATION,
        PipelineStageId.CANDIDATE_VALIDATION,
    )
    assert not (tmp_path / "manifests" / f"{PipelineStageId.COARSE_CHARACTERIZATION}.json").exists()


def test_a_stage_that_runs_tasks_in_the_worker_pool_gives_the_same_information_with_1_or_2_workers(tmp_path):
    """A stage whose tasks run in this process or in 2 workers stores the same c-ranges; each manifest records its
    run's number of workers."""
    # --- act --------------------------
    results = []
    for n_workers in (1, 2):
        with WorkerPool(n_workers=n_workers) as worker_pool:
            results.append(
                run_stages(
                    PipelineWorkspace(tmp_path / f"{n_workers}_workers"),
                    [_ExampleGenerationStage(), _ExampleValidationStage()],
                    worker_pool=worker_pool,
                )
            )

    # --- assert -----------------------
    in_process_result, worker_processes_result = results
    c_ranges = [
        result.state.create_state_accessor(PipelineStageId.COARSE_CHARACTERIZATION).c_ranges() for result in results
    ]
    assert c_ranges[0] == c_ranges[1]
    assert (in_process_result.manifests[-1].n_workers, worker_processes_result.manifests[-1].n_workers) == (1, 2)
