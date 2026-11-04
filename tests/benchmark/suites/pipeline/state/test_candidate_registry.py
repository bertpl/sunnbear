"""`CandidateRegistry` keeps every candidate in the order in which it was added, with the drop of each dropped one,
and refuses to add a candidate twice or to drop a candidate that is not remaining."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.state import CandidateDrop, CandidateRegistry
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

_DROP = CandidateDrop(stage_id=PipelineStageId.SPACING, reason="near_duplicate", is_rejection=False)


def test_a_dropped_candidate_keeps_its_entry_with_its_drop():
    """After 1 of 3 candidates is dropped, every candidate stays in the registry, the other 2 remain, and the drop
    names the stage that made it."""
    # --- arrange ----------------------
    registry = CandidateRegistry()
    problem_ids = example_problem_ids(3)
    registry.add(problem_ids)

    # --- act --------------------------
    registry.record_drop(problem_ids[1], _DROP)

    # --- assert -----------------------
    assert registry.problem_ids == tuple(problem_ids)
    assert registry.remaining_problem_ids == (problem_ids[0], problem_ids[2])
    assert (registry.drop_of(problem_ids[0]), registry.drop_of(problem_ids[1])) == (None, _DROP)
    assert registry.problem_ids_dropped_by(PipelineStageId.SPACING) == (problem_ids[1],)
    assert registry.problem_ids_dropped_by(PipelineStageId.CORE_SELECTION) == ()


@pytest.mark.parametrize("is_added_before", [False, True], ids=["repeated_in_1_call", "added_before"])
def test_the_registry_holds_each_candidate_once(is_added_before: bool):
    """A candidate that repeats in 1 call, or that was added before, is refused."""
    # --- arrange ----------------------
    registry = CandidateRegistry()
    problem_ids = example_problem_ids(2)
    if is_added_before:
        registry.add(problem_ids)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="each candidate once"):
        registry.add(problem_ids if is_added_before else [problem_ids[0], problem_ids[0]])


@pytest.mark.parametrize(
    "is_dropped_before, message",
    [(False, "not a candidate of the registry"), (True, "dropped already")],
    ids=["unknown", "dropped_before"],
)
def test_only_a_remaining_candidate_can_be_dropped(is_dropped_before: bool, message: str):
    """Dropping a candidate that the registry does not hold, or one dropped before, is refused."""
    # --- arrange ----------------------
    registry = CandidateRegistry()
    [problem_id, unknown_problem_id] = example_problem_ids(2)
    registry.add([problem_id])
    if is_dropped_before:
        registry.record_drop(problem_id, _DROP)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        registry.record_drop(problem_id if is_dropped_before else unknown_problem_id, _DROP)
