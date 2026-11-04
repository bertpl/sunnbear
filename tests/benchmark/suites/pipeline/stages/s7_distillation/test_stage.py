"""`DistillationStage` distills a benchmark family and a calibration family of nested suites from the Core:

- the 2 families split the Core in halves, and every suite meets the Core's quotas at its size;
- each family's smaller suites lie inside its larger ones, also when Da and Db share 1 quota;
- the stage records max-div's time per candidate and seed in its parameters.
"""

from collections import Counter

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import CoreCompositionWarning, DifficultyClass, SuiteFamily
from sunnbear._core.benchmark.suites.pipeline.stages import DistillationStage
from sunnbear._core.benchmark.suites.pipeline.state import (
    DistillationStateAccessor,
    DistilledSuiteSummary,
    SuiteMembership,
)
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids, record_calls

A, B, C, DA, DB = DifficultyClass

# The stage runs no tasks in the pool, so the pool's processes never start. max-div runs 1 worker per worker of the
# pool, and with 1 worker it warns that it gains nothing over a single solve, so the pool has 2 workers.
_TWO_WORKER_POOL = WorkerPool(n_workers=2)
# Each max-div worker runs this long per candidate of the pool it selects from; with the pools of 128 and 256
# candidates in these tests, that covers the start of the workers' processes and leaves time to meet every quota on
# a busy CI machine.
_SEC_PER_CANDIDATE = 0.03
# The range of each class's EDIs, relative to `DEFAULT_N_BISECTION_FEVALS`; the EDIs differ within a class, so that the
# distance between 2 EDIs of 1 class is not 0.
_EDI_RATIO_RANGE_BY_CLASS = {A: (0.1, 0.2), B: (0.3, 0.45), C: (0.6, 0.9), DA: (1.2, 1.8), DB: (2.5, 3.5)}


def _distill(
    class_counts: dict[DifficultyClass, int], stage: DistillationStage, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[ProblemId, DifficultyClass], dict[ProblemId, SuiteMembership], tuple[DistilledSuiteSummary, ...]]:
    """Run `stage` on a Core with `class_counts` candidates of each class; return their classes, memberships and
    suites."""
    classes = [c for c, count in class_counts.items() for _ in range(count)]
    problem_ids = example_problem_ids(len(classes))
    rng = np.random.default_rng(seed=4)
    edis = {
        problem_id: rng.uniform(*_EDI_RATIO_RANGE_BY_CLASS[c]) * DEFAULT_N_BISECTION_FEVALS
        for problem_id, c in zip(problem_ids, classes, strict=True)
    }
    state = build_state_before(PipelineStageId.DISTILLATION, problem_ids, edis=edis)
    memberships_calls = record_calls(monkeypatch, DistillationStateAccessor, "set_suite_memberships")
    suites_calls = record_calls(monkeypatch, DistillationStateAccessor, "set_distilled_suite_summaries")
    stage.run(state.create_state_accessor(PipelineStageId.DISTILLATION), worker_pool=_TWO_WORKER_POOL)
    [(memberships,)], [(suites,)] = memberships_calls, suites_calls
    return dict(zip(problem_ids, classes, strict=True)), dict(memberships), tuple(suites)


def _class_counts(
    classes: dict[ProblemId, DifficultyClass],
    memberships: dict[ProblemId, SuiteMembership],
    family: SuiteFamily,
    size: int,
) -> dict[DifficultyClass, int]:
    """Return the number of candidates per class of the suite of `family` and `size`."""
    counts = Counter(
        classes[problem_id]
        for problem_id, membership in memberships.items()
        if membership.suite_family is family and membership.smallest_containing_suite_size <= size
    )
    return {c: counts[c] for c in DifficultyClass}


@pytest.mark.only_with_numba_jit
def test_the_families_split_a_core_of_128_into_2_suites_of_64(monkeypatch):
    """A Core of 128 with 1 quota per class splits into a benchmark suite and a calibration suite of 64, each with 16
    of A, B and C, 12 of Da and 4 of Db; only the benchmark suite has a diversity score."""
    # --- act --------------------------
    classes, memberships, suites = _distill(
        {A: 32, B: 32, C: 32, DA: 24, DB: 8}, DistillationStage(_SEC_PER_CANDIDATE), monkeypatch
    )

    # --- assert -----------------------
    assert set(memberships) == set(classes)
    assert all(membership.smallest_containing_suite_size == 64 for membership in memberships.values())
    for family in SuiteFamily:
        assert _class_counts(classes, memberships, family, 64) == {A: 16, B: 16, C: 16, DA: 12, DB: 4}
    assert [(suite.suite_family, suite.size) for suite in suites] == [
        (SuiteFamily.BENCHMARK, 64),
        (SuiteFamily.CALIBRATION, 64),
    ]
    assert suites[0].diversity > 0.0
    assert suites[1].diversity is None


@pytest.mark.only_with_numba_jit
def test_each_family_nests_its_suites_under_a_shared_quota_and_records_its_parameters(monkeypatch):
    """A Core of 256 whose classes Da and Db share 1 quota splits into 2 families of 128; each family's suite of 64 is
    a subset of its suite of 128, with 16 each of A, B and C and 16 of Da and Db together; the stage's parameters
    record max-div's time per candidate and seed."""
    # --- arrange ----------------------
    stage = DistillationStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    # The example state composes the Core from the classes, which warns that Da and Db share 1 quota.
    with pytest.warns(CoreCompositionWarning):
        classes, memberships, suites = _distill({A: 64, B: 64, C: 64, DA: 40, DB: 24}, stage, monkeypatch)

    # --- assert -----------------------
    for family in SuiteFamily:
        for size, quota_expected in [(128, 32), (64, 16)]:
            counts = _class_counts(classes, memberships, family, size)
            assert [counts[A], counts[B], counts[C], counts[DA] + counts[DB]] == [quota_expected] * 4
    assert [(suite.suite_family, suite.size) for suite in suites] == [
        (SuiteFamily.BENCHMARK, 128),
        (SuiteFamily.BENCHMARK, 64),
        (SuiteFamily.CALIBRATION, 128),
        (SuiteFamily.CALIBRATION, 64),
    ]
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}
