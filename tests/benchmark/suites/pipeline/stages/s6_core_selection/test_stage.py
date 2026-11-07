"""`CoreSelectionStage` selects the Core from the candidates' full features:

- it stores each candidate's difficulty class, from its EDI;
- it selects the Core by max-div under the difficulty quotas, also when Da and Db share 1 quota, and drops the other
  candidates;
- it records max-div's time per candidate and seed in its parameters.
"""

from collections import Counter

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import CoreCompositionWarning, DifficultyClass
from sunnbear._core.benchmark.suites.pipeline.stages import CoreSelectionStage
from sunnbear._core.benchmark.suites.pipeline.state import PipelineState
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids

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


@pytest.mark.only_with_numba_jit
def test_the_stage_selects_a_core_that_meets_every_quota():
    """From 160 candidates whose EDIs fall 40 each in A, B and C, 30 in Da and 10 in Db, the stage selects a Core of
    128 with 32 each of A, B and C, 24 of Da and 8 of Db, an interim Core because it is smaller than 2048; it drops
    the other 32 candidates as not in the Core."""
    # --- arrange ----------------------
    edis = [5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 30 + [120.0] * 10

    # --- act --------------------------
    state = _select_core(edis, CoreSelectionStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    distillation_accessor = state.create_state_accessor(PipelineStageId.DISTILLATION)
    core_classes = Counter(distillation_accessor.candidate_pool().difficulty_classes)
    assert core_classes == {
        DifficultyClass.A: 32,
        DifficultyClass.B: 32,
        DifficultyClass.C: 32,
        DifficultyClass.DA: 24,
        DifficultyClass.DB: 8,
    }
    summary = distillation_accessor.core_composition().summary()
    assert [summary[key] for key in ("core_size", "is_interim", "quota_a", "quota_da", "quota_db", "quota_d")] == [
        128,
        True,
        32,
        24,
        8,
        None,
    ]
    drops = [state.drop_of(problem_id) for problem_id in example_problem_ids(len(edis))]
    assert Counter(drop.reason for drop in drops if drop is not None) == {"not_in_core": 32}


@pytest.mark.only_with_numba_jit
def test_the_stage_fills_a_shared_quota_and_records_its_parameters():
    """The candidates hold no Db, so Da and Db share 1 quota, with a warning, and the selection fills it; the stage's
    parameters record max-div's time per candidate and seed."""
    # --- arrange ----------------------
    stage = CoreSelectionStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    with pytest.warns(CoreCompositionWarning):
        state = _select_core([5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 40, stage)

    # --- assert -----------------------
    core_classes = Counter(
        state.create_state_accessor(PipelineStageId.DISTILLATION).candidate_pool().difficulty_classes
    )
    assert core_classes == dict.fromkeys(
        [DifficultyClass.A, DifficultyClass.B, DifficultyClass.C, DifficultyClass.DA], 32
    )
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}
