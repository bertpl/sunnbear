"""`PipelineState` creates each stage's accessor in run order, once every earlier stage has finished, and gives each
candidate's drop."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass
from sunnbear._core.benchmark.suites.pipeline.state import (
    CandidateDrop,
    CandidateGenerationStateAccessor,
    DistillationStateAccessor,
    PipelineState,
)
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids


def test_the_state_creates_each_stages_accessor_in_run_order():
    """The first accessor is candidate generation's; once every stage before distillation has finished, the state
    creates distillation's accessor, and records the stages that finished."""
    # --- arrange ----------------------
    state = build_state_before(
        PipelineStageId.DISTILLATION,
        example_problem_ids(4),
        core_composition=CoreComposition.from_class_counts(dict.fromkeys(DifficultyClass, 64)),
    )

    # --- act --------------------------
    first_accessor = PipelineState().create_accessor(PipelineStageId.CANDIDATE_GENERATION)
    last_accessor = state.create_accessor(PipelineStageId.DISTILLATION)

    # --- assert -----------------------
    assert type(first_accessor) is CandidateGenerationStateAccessor
    assert type(last_accessor) is DistillationStateAccessor
    assert state.finished_stage_ids == tuple(PipelineStageId)[:-1]


def test_the_state_refuses_an_accessor_out_of_run_order():
    """An accessor for a stage whose earlier stage has not finished, or a second accessor for the same stage, is
    refused."""
    # --- arrange ----------------------
    state = PipelineState()
    state.create_accessor(PipelineStageId.CANDIDATE_GENERATION)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="the next stage to run is s1_candidate_generation"):
        state.create_accessor(PipelineStageId.CANDIDATE_VALIDATION)
    with pytest.raises(ValueError, match="the next stage to run is s1_candidate_generation"):
        state.create_accessor(PipelineStageId.CANDIDATE_GENERATION)


@pytest.mark.parametrize("is_started", [False, True], ids=["not_started", "finished_before"])
def test_a_stage_finishes_once_after_it_starts(is_started: bool):
    """Finishing a stage without an accessor, or finishing it twice, is refused."""
    # --- arrange ----------------------
    state = PipelineState()
    if is_started:
        state.create_accessor(PipelineStageId.CANDIDATE_GENERATION)
        state.finish_stage(PipelineStageId.CANDIDATE_GENERATION)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="has not started, or has finished already"):
        state.finish_stage(PipelineStageId.CANDIDATE_GENERATION)


def test_the_state_gives_each_candidates_drop():
    """A candidate that validation rejects has its drop, and a remaining candidate has none."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(2)
    state = build_state_before(PipelineStageId.CANDIDATE_VALIDATION, problem_ids)

    # --- act --------------------------
    state.create_accessor(PipelineStageId.CANDIDATE_VALIDATION).reject(problem_ids[0], "bound_to_width_ratio")

    # --- assert -----------------------
    assert state.drop_of(problem_ids[0]) == CandidateDrop(
        stage_id=PipelineStageId.CANDIDATE_VALIDATION, reason="bound_to_width_ratio", is_rejection=True
    )
    assert state.drop_of(problem_ids[1]) is None
    assert state.n_remaining_candidates == 1
