"""`CoreSelectionStage` selects the Core from the candidates' fine features:

- the Core's size is the largest of `CORE_SIZES` that the candidates fill, and the stage stops the pipeline below it;
- it stores each candidate's tier, from its EDI;
- it selects the Core by max-div under the tier quotas, also when a tier is short, drops the other candidates, and
  stores the Core's selection details;
- it records max-div's time per candidate and seed in its parameters.
"""

from collections import Counter

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier
from sunnbear._core.benchmark.suites.pipeline.stages import CoreSelectionStage
from sunnbear._core.benchmark.suites.pipeline.state import PipelineState
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids

A, B, C, DA, DB = DifficultyTier

# The stage runs no tasks in the pool, so its processes never start; max-div runs 1 worker per worker of the pool, and
# warns that 1 worker gains nothing over a single solve.
_TWO_WORKER_POOL = WorkerPool(n_workers=2)
# In these tests each max-div worker runs for 8 s on 160 candidates, which covers the start of the workers' processes
# and leaves time to meet every quota on a busy CI machine.
_SEC_PER_CANDIDATE = 0.05


def _select_core(edis: list[float], stage: CoreSelectionStage) -> PipelineState:
    """Run `stage` on 1 example candidate per EDI of `edis`, and return the state after it."""
    problem_ids = example_problem_ids(len(edis))
    state = build_state_before(
        PipelineStageId.CORE_SELECTION, problem_ids, edis=dict(zip(problem_ids, edis, strict=True))
    )
    state.run_stage(stage, worker_pool=_TWO_WORKER_POOL)
    return state


@pytest.mark.parametrize(
    "n_candidates, core_size_expected",
    [
        pytest.param(128, 128, id="smallest"),
        pytest.param(300, 256, id="between_sizes"),
        pytest.param(9999, 2048, id="capped_at_2048"),
    ],
)
def test_the_core_size_is_the_largest_that_the_candidates_fill(n_candidates, core_size_expected):
    """The Core's size is the largest of `CORE_SIZES` at or below the number of candidates."""
    # --- act / assert -----------------
    assert CoreSelectionStage._choose_core_size(n_candidates) == core_size_expected


def test_the_stage_stops_the_pipeline_below_the_smallest_core_size():
    """The stage stops the pipeline for 127 candidates, which fill no Core of 128, and the message gives the 127."""
    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"^The candidates fill no Core of 128 or more: there are 127\.$"):
        _select_core([5.0] * 127, CoreSelectionStage(_SEC_PER_CANDIDATE))


@pytest.mark.only_with_numba_jit
def test_the_stage_selects_a_core_that_meets_every_quota():
    """From 160 candidates whose EDIs fall 40 each in A, B and C, 30 in Da and 10 in Db, the stage selects the Core
    `sb-128` with 32 each of A, B and C, 24 of Da and 8 of Db under 1 quota per tier, and drops the other 32 candidates
    as not in the Core."""
    # --- arrange ----------------------
    edis = [5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 30 + [120.0] * 10

    # --- act --------------------------
    state = _select_core(edis, CoreSelectionStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    core_pool = state.create_state_accessor(PipelineStageId.DISTILLATION).candidate_pool()
    assert Counter(core_pool.difficulty_tiers.values()) == {A: 32, B: 32, C: 32, DA: 24, DB: 8}
    core_selection_details = state.create_build_details().core_selection_details()
    assert core_selection_details.benchmark_suite.name == "sb-128"
    assert core_selection_details.benchmark_suite.aliases == ()
    assert core_selection_details.edi_range_by_tier == {
        A: (5.0, 5.0),
        B: (15.0, 15.0),
        C: (30.0, 30.0),
        DA: (60.0, 60.0),
        DB: (120.0, 120.0),
    }
    drops = [state.drop_of(problem_id) for problem_id in example_problem_ids(len(edis))]
    assert Counter(drop.reason for drop in drops if drop is not None) == {"not_in_core": 32}


@pytest.mark.only_with_numba_jit
def test_the_stage_fills_a_short_tier_from_its_neighbor_and_records_its_parameters():
    """No candidate is of tier Db, and all candidates of Da share the EDI 60, so the last 8 of Da in the pool count
    toward Db's quota, and the Core holds all 8; the stage's parameters record max-div's time per candidate and seed."""
    # --- arrange ----------------------
    stage = CoreSelectionStage(_SEC_PER_CANDIDATE)
    edis = [5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 40

    # --- act --------------------------
    state = _select_core(edis, stage)

    # --- assert -----------------------
    core_pool = state.create_state_accessor(PipelineStageId.DISTILLATION).candidate_pool()
    assert Counter(core_pool.difficulty_tiers.values()) == dict.fromkeys([A, B, C, DA], 32)
    core_selection_details = state.create_build_details().core_selection_details()
    assert set(example_problem_ids(len(edis))[-8:]) <= set(core_selection_details.benchmark_suite.problem_ids)
    assert core_selection_details.edi_range_by_tier[DB] == (60.0, 60.0)
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}
