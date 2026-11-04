"""`SpacingStage` drops near-duplicate candidates of each formula:

- it keeps, in the order of candidate generation, the candidates at least `min_distance` apart in the scaled coarse
  feature space;
- it keeps at least 2 candidates of every formula that has 2 or more;
- it stores each dropped candidate's nearest kept candidate.

The tests give the stage its scaled coarse features directly, not those that the state computes.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.stages import SpacingStage
from sunnbear._core.benchmark.suites.pipeline.state import CandidateDrop, NearestKeptCandidate, SpacingStateAccessor
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, record_calls

_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)
_NEAR_DUPLICATE = CandidateDrop(stage_id=PipelineStageId.SPACING, reason="near_duplicate", is_rejection=False)


def _run_spacing(
    vectors_by_problem_id: dict[str, tuple[float, ...]] | None,
    monkeypatch: pytest.MonkeyPatch,
    *,
    problem_ids: list[str] | None = None,
) -> tuple[dict[ProblemId, CandidateDrop | None], dict[ProblemId, NearestKeptCandidate]]:
    """Run spacing at a minimum distance of 1 on the scaled features `vectors_by_problem_id`; return each candidate's
    drop and the stored nearest kept candidates.

    `vectors_by_problem_id` ``None`` stands for a coarse characterization without scales, of the candidates
    `problem_ids`.
    """
    if vectors_by_problem_id is not None:
        problem_ids = list(vectors_by_problem_id)
        scaled_feature_matrix = FeatureMatrix(
            problem_ids=tuple(map(ProblemId.from_string, problem_ids)),
            values=np.array(list(vectors_by_problem_id.values())),
        )
    else:
        scaled_feature_matrix = None
    monkeypatch.setattr(SpacingStateAccessor, "coarse_scaled_feature_matrix", lambda self: scaled_feature_matrix)
    calls = record_calls(monkeypatch, SpacingStateAccessor, "set_nearest_kept_candidates")
    state = build_state_before(PipelineStageId.SPACING, [ProblemId.from_string(p) for p in problem_ids])

    state.run_stage(SpacingStage(min_distance=1.0), worker_pool=_IN_PROCESS_WORKER_POOL)

    [(nearest_kept_candidates,)] = calls
    drops = {ProblemId.from_string(p): state.drop_of(ProblemId.from_string(p)) for p in problem_ids}
    return drops, dict(nearest_kept_candidates)


def test_the_pass_keeps_the_candidates_far_enough_from_every_kept_one_in_order(monkeypatch):
    """The stage's pass over the candidates keeps p=1, p=3 and p=5 of formula f99.1, and drops p=2 and p=4, each closer
    than 1 to the kept candidate before it; p=3 is kept over p=4 because it comes first.

    Formula f99.2's only candidate is kept, although it coincides with f99.1's first candidate."""
    # --- act --------------------------
    drops, nearest_kept_candidates = _run_spacing(
        {
            "f99.1[p=1.0]": (0.0, 0.0),
            "f99.1[p=2.0]": (0.6, 0.0),  # p=2 lies at 0.6 from p=1
            "f99.1[p=3.0]": (0.6, 0.6),  # p=3 lies at 1.2 from p=1
            "f99.1[p=4.0]": (1.2, 0.6),  # p=4 lies at 0.6 from p=3
            "f99.1[p=5.0]": (1.5, 1.0),  # p=5 lies at 1.3 from p=3
            "f99.2": (0.0, 0.0),
        },
        monkeypatch,
    )

    # --- assert -----------------------
    dropped_problem_ids = [problem_id for problem_id, drop in drops.items() if drop is not None]
    assert [str(problem_id) for problem_id in dropped_problem_ids] == ["f99.1[p=2.0]", "f99.1[p=4.0]"]
    assert all(drops[problem_id] == _NEAR_DUPLICATE for problem_id in dropped_problem_ids)
    assert {str(p): (str(n.problem_id), n.distance) for p, n in nearest_kept_candidates.items()} == {
        "f99.1[p=2.0]": ("f99.1[p=1.0]", pytest.approx(0.6)),
        "f99.1[p=4.0]": ("f99.1[p=3.0]", pytest.approx(0.6)),
    }


def test_a_formula_with_2_or_more_candidates_keeps_at_least_2(monkeypatch):
    """Where the pass keeps only a formula's first candidate, the stage also keeps the one farthest from it: for f99.1
    that is p=3, which then becomes the nearest kept candidate of p=2; for f99.2 it is the second of its 2 identical
    candidates."""
    # --- act --------------------------
    drops, nearest_kept_candidates = _run_spacing(
        {
            "f99.1[p=1.0]": (0.0, 0.0),
            "f99.1[p=2.0]": (0.2, 0.0),  # p=2 lies at 0.2 from p=1 and 0.1 from p=3
            "f99.1[p=3.0]": (0.3, 0.0),  # p=3 lies at 0.3 from p=1
            "f99.2[p=1.0]": (0.0, 0.0),
            "f99.2[p=2.0]": (0.0, 0.0),
        },
        monkeypatch,
    )

    # --- assert -----------------------
    assert [str(problem_id) for problem_id, drop in drops.items() if drop is not None] == ["f99.1[p=2.0]"]
    assert {str(p): (str(n.problem_id), n.distance) for p, n in nearest_kept_candidates.items()} == {
        "f99.1[p=2.0]": ("f99.1[p=3.0]", pytest.approx(0.1))
    }


def test_without_scales_every_candidate_is_kept(monkeypatch):
    """Coarse characterization has no scales when it keeps fewer than 2 candidates; the stage then keeps every
    candidate, and stores no nearest kept candidate."""
    # --- act --------------------------
    drops, nearest_kept_candidates = _run_spacing(None, monkeypatch, problem_ids=["f99.1"])

    # --- assert -----------------------
    assert drops == {ProblemId.from_string("f99.1"): None}
    assert nearest_kept_candidates == {}
