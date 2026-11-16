"""`SpacingStage` drops near-duplicate candidates of each formula:

- per formula, its pass goes through the candidates in ascending order of their coarse EDI, always keeps the first and
  the last, and keeps each candidate in between that lies at least the minimum distance from every kept one;
- it chooses the largest minimum distance at which it keeps at least its target number of candidates;
- it stores the minimum distance, and each dropped candidate's nearest kept candidate.

The tests give the stage its scaled coarse features directly, not those that the state computes.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.stages import SPACING_MIN_DISTANCE_OPTIONS, SpacingStage, s4_spacing
from sunnbear._core.benchmark.suites.pipeline.state import CandidateDrop, NearestKeptCandidate, SpacingStateAccessor
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, record_calls

_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)
_NEAR_DUPLICATE = CandidateDrop(stage_id=PipelineStageId.SPACING, reason="near_duplicate", is_rejection=False)


def _run_spacing(
    candidates: dict[str, tuple[float, tuple[float, ...]]] | None,
    monkeypatch: pytest.MonkeyPatch,
    *,
    target_n_kept_candidates: int,
    problem_ids: list[str] | None = None,
) -> tuple[dict[ProblemId, CandidateDrop | None], dict[ProblemId, NearestKeptCandidate], float]:
    """Run spacing on `candidates`; return each candidate's drop, the stored nearest kept candidates and the stored
    minimum distance.

    `candidates` maps each problem id to the candidate's coarse EDI and scaled feature vector. ``None`` stands for a
    coarse characterization without scales, of the candidates `problem_ids`.
    """
    if candidates is not None:
        problem_ids = list(candidates)
        scaled_feature_matrix = FeatureMatrix(
            problem_ids=tuple(map(ProblemId.from_string, problem_ids)),
            values=np.array([vector for _, vector in candidates.values()]),
        )
        edis = {ProblemId.from_string(problem_id): edi for problem_id, (edi, _) in candidates.items()}
    else:
        scaled_feature_matrix = None
        edis = None
    monkeypatch.setattr(SpacingStateAccessor, "coarse_scaled_feature_matrix", lambda self: scaled_feature_matrix)
    nearest_kept_candidates_calls = record_calls(monkeypatch, SpacingStateAccessor, "set_nearest_kept_candidates")
    min_distance_calls = record_calls(monkeypatch, SpacingStateAccessor, "set_min_distance")
    state = build_state_before(PipelineStageId.SPACING, [ProblemId.from_string(p) for p in problem_ids], edis=edis)

    state.run_stage(
        SpacingStage(target_n_kept_candidates=target_n_kept_candidates), worker_pool=_IN_PROCESS_WORKER_POOL
    )

    [(nearest_kept_candidates,)], [(min_distance,)] = nearest_kept_candidates_calls, min_distance_calls
    drops = {ProblemId.from_string(p): state.drop_of(ProblemId.from_string(p)) for p in problem_ids}
    return drops, dict(nearest_kept_candidates), min_distance


def test_the_pass_goes_in_edi_order_and_keeps_the_candidates_far_enough_from_every_kept_one(monkeypatch):
    """At a minimum distance of 1, formula f99.1 keeps p=2 and p=3, its candidates with the lowest and the highest EDI,
    and p=4, which lies at least 1 from both. It drops p=1, closer than 1 to p=2, and p=5, closer than 1 to p=3.

    Formula f99.2's only candidate is kept, although it coincides with a kept candidate of f99.1."""
    # --- arrange ----------------------
    monkeypatch.setattr(s4_spacing, "SPACING_MIN_DISTANCE_OPTIONS", (1.0,))

    # --- act --------------------------
    drops, nearest_kept_candidates, _ = _run_spacing(
        {
            "f99.1[p=1.0]": (20.0, (0.6, 0.0)),  # p=1 lies at 0.6 from p=2
            "f99.1[p=2.0]": (10.0, (0.0, 0.0)),  # the lowest EDI
            "f99.1[p=3.0]": (50.0, (3.0, 0.0)),  # the highest EDI
            "f99.1[p=4.0]": (30.0, (1.2, 0.0)),  # p=4 lies at 1.2 from p=2 and at 1.8 from p=3
            "f99.1[p=5.0]": (40.0, (2.5, 0.0)),  # p=5 lies at 0.5 from p=3
            "f99.2": (10.0, (0.0, 0.0)),
        },
        monkeypatch,
        target_n_kept_candidates=1,
    )

    # --- assert -----------------------
    dropped_problem_ids = [problem_id for problem_id, drop in drops.items() if drop is not None]
    assert [str(problem_id) for problem_id in dropped_problem_ids] == ["f99.1[p=1.0]", "f99.1[p=5.0]"]
    assert all(drops[problem_id] == _NEAR_DUPLICATE for problem_id in dropped_problem_ids)
    assert {str(p): (str(n.problem_id), n.distance) for p, n in nearest_kept_candidates.items()} == {
        "f99.1[p=1.0]": ("f99.1[p=2.0]", pytest.approx(0.6)),
        "f99.1[p=5.0]": ("f99.1[p=3.0]", pytest.approx(0.5)),
    }


def test_the_first_and_the_last_candidate_are_kept_whatever_their_distance(monkeypatch):
    """Candidates with equal EDIs keep the order of candidate generation, so p=1 and p=3 are f99.1's first and last
    candidate: the stage keeps both, although they lie closer together than the minimum distance of 1, and drops p=2.
    Formula f99.2 keeps both of its 2 identical candidates."""
    # --- arrange ----------------------
    monkeypatch.setattr(s4_spacing, "SPACING_MIN_DISTANCE_OPTIONS", (1.0,))

    # --- act --------------------------
    drops, nearest_kept_candidates, _ = _run_spacing(
        {
            "f99.1[p=1.0]": (10.0, (0.0, 0.0)),
            "f99.1[p=2.0]": (10.0, (0.3, 0.0)),  # p=2 lies at 0.3 from p=1 and at 0.1 from p=3
            "f99.1[p=3.0]": (10.0, (0.2, 0.0)),
            "f99.2[p=1.0]": (10.0, (0.0, 0.0)),
            "f99.2[p=2.0]": (10.0, (0.0, 0.0)),
        },
        monkeypatch,
        target_n_kept_candidates=1,
    )

    # --- assert -----------------------
    assert [str(problem_id) for problem_id, drop in drops.items() if drop is not None] == ["f99.1[p=2.0]"]
    assert {str(p): (str(n.problem_id), n.distance) for p, n in nearest_kept_candidates.items()} == {
        "f99.1[p=2.0]": ("f99.1[p=3.0]", pytest.approx(0.1))
    }


@pytest.mark.parametrize(
    "target_n_kept_candidates, exponent_expected, n_kept_expected",
    [
        pytest.param(2, 1.0, 2, id="every_option_reaches_the_target"),
        pytest.param(3, -0.4, 3, id="options_up_to_0.5_reach_the_target"),
        pytest.param(4, -1.4, 4, id="options_up_to_0.05_reach_the_target"),
        pytest.param(5, -3.0, 4, id="no_option_reaches_the_target"),
    ],
)
def test_the_stage_chooses_the_largest_min_distance_that_keeps_the_target(
    monkeypatch, target_n_kept_candidates: int, exponent_expected: float, n_kept_expected: int
):
    """The formula's 4 candidates lie on a line at 0, 0.05, 0.5 and 5, in the order of their EDIs, so the stage keeps
    4 of them at a minimum distance up to 0.05, 3 up to 0.5, and 2 above 0.5.

    For each target, the stage chooses the largest option at which it keeps at least the target; for a target of 5,
    which no option reaches, it chooses the smallest option."""
    # --- act --------------------------
    drops, _, min_distance = _run_spacing(
        {
            "f99.1[p=1.0]": (10.0, (0.0, 0.0)),
            "f99.1[p=2.0]": (20.0, (0.05, 0.0)),
            "f99.1[p=3.0]": (30.0, (0.5, 0.0)),
            "f99.1[p=4.0]": (40.0, (5.0, 0.0)),
        },
        monkeypatch,
        target_n_kept_candidates=target_n_kept_candidates,
    )

    # --- assert -----------------------
    assert min_distance == pytest.approx(10.0**exponent_expected)
    assert min_distance in SPACING_MIN_DISTANCE_OPTIONS
    assert list(drops.values()).count(None) == n_kept_expected


def test_the_min_distance_options_run_from_a_thousandth_to_10_in_steps_of_a_tenth_of_a_decade():
    """The 41 options are 10^-3.0, 10^-2.9, ... up to 10^1.0."""
    # --- act / assert -----------------
    np.testing.assert_allclose(np.log10(SPACING_MIN_DISTANCE_OPTIONS), np.linspace(-3.0, 1.0, 41), atol=1e-12)


def test_without_scales_every_candidate_is_kept(monkeypatch):
    """Coarse characterization has no scales when it keeps fewer than 2 candidates; the stage then keeps every
    candidate, stores no nearest kept candidate, and stores the smallest option as its minimum distance."""
    # --- act --------------------------
    drops, nearest_kept_candidates, min_distance = _run_spacing(
        None, monkeypatch, target_n_kept_candidates=1, problem_ids=["f99.1"]
    )

    # --- assert -----------------------
    assert drops == {ProblemId.from_string("f99.1"): None}
    assert nearest_kept_candidates == {}
    assert min_distance == min(SPACING_MIN_DISTANCE_OPTIONS)
