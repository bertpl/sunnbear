"""`DistillationStage` distills an a-series and a b-series of nested suites from the Core:

- the 2 series split the Core in halves; each suite has its name, and the a-series' suites their aliases;
- each series' smaller suites lie inside its larger ones;
- every suite that a selection makes meets the quotas that the stage stores for it;
- the stage records max-div's time per candidate and seed in its parameters;
- the a-series' aliases cover each of its sizes in the largest Core.
"""

from collections import Counter
from itertools import pairwise

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier
from sunnbear._core.benchmark.suites.pipeline.stages import SMALLEST_SUITE_SIZE, DistillationStage
from sunnbear._core.benchmark.suites.pipeline.stages.s6_core_selection import CORE_SIZES
from sunnbear._core.benchmark.suites.pipeline.stages.s7_distillation.stage import _PRIMARY_SERIES_ALIASES
from sunnbear._core.benchmark.suites.pipeline.state import BenchmarkSuitesBuildDetails
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids

A, B, C, DA, DB = DifficultyTier

# The stage runs no tasks in the pool, so the pool's processes never start. max-div runs 1 worker per worker of the
# pool, and with 1 worker it warns that it gains nothing over a single solve, so the pool has 2 workers.
_TWO_WORKER_POOL = WorkerPool(n_workers=2)
# Each max-div worker runs this long per candidate of the pool it selects from; with the pools of 128 and 256
# candidates in these tests, that covers the start of the workers' processes and leaves time to meet every quota on
# a busy CI machine.
_SEC_PER_CANDIDATE = 0.03
# These are the ranges of each tier's EDIs, relative to `DEFAULT_N_BISECTION_FEVALS`; the EDIs differ within a tier,
# so that the distance between 2 EDIs of 1 tier is not 0.
_EDI_RATIO_RANGE_BY_TIER = {A: (0.1, 0.2), B: (0.3, 0.45), C: (0.6, 0.9), DA: (1.2, 1.8), DB: (2.5, 3.5)}


def _distill(tier_counts: dict[DifficultyTier, int], stage: DistillationStage) -> BenchmarkSuitesBuildDetails:
    """Run `stage` on a Core with `tier_counts` candidates of each tier, and return the build details of the run."""
    tiers = [tier for tier, count in tier_counts.items() for _ in range(count)]
    problem_ids = example_problem_ids(len(tiers))
    rng = np.random.default_rng(seed=4)
    edis = {
        problem_id: rng.uniform(*_EDI_RATIO_RANGE_BY_TIER[tier]) * DEFAULT_N_BISECTION_FEVALS
        for problem_id, tier in zip(problem_ids, tiers, strict=True)
    }
    state = build_state_before(PipelineStageId.DISTILLATION, problem_ids, edis=edis)
    state.run_stage(stage, worker_pool=_TWO_WORKER_POOL)
    return state.create_build_details()


def _check_quotas_and_nesting(build_details: BenchmarkSuitesBuildDetails) -> None:
    """Check that each suite that a selection makes meets its quotas, and that each suite holds the next smaller one of
    its series."""
    difficulty_tiers = build_details.difficulty_tiers()
    all_selection_details = list(build_details.distilled_suite_selection_details().values())
    for selection_details, next_selection_details in pairwise(all_selection_details):
        suite, next_suite = selection_details.benchmark_suite, next_selection_details.benchmark_suite
        if suite.name[-1] == next_suite.name[-1]:
            assert set(next_suite.problem_ids) < set(suite.problem_ids)
    for selection_details in all_selection_details:
        if selection_details.tier_quotas is not None:
            tier_counts = Counter(difficulty_tiers[p] for p in selection_details.benchmark_suite.problem_ids)
            for tiers, count in selection_details.tier_quotas.quota_by_group.items():
                assert sum(tier_counts[tier] for tier in tiers) == count


@pytest.mark.only_with_numba_jit
def test_the_series_split_a_core_of_128_into_2_suites_of_64():
    """A Core of 128 with every tier at its share splits into `sb-64a`, alias `sb-tiny`, and `sb-64b`, each with 16
    of A, B and C, 12 of Da and 4 of Db; only `sb-64a` has quotas and a diversity score."""
    # --- act --------------------------
    build_details = _distill({A: 32, B: 32, C: 32, DA: 24, DB: 8}, DistillationStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    all_selection_details = build_details.distilled_suite_selection_details()
    assert [(name, details.benchmark_suite.aliases) for name, details in all_selection_details.items()] == [
        ("sb-64a", ("sb-tiny",)),
        ("sb-64b", ()),
    ]
    a_suite, b_suite = (details.benchmark_suite for details in all_selection_details.values())
    assert set(a_suite.problem_ids) | set(b_suite.problem_ids) == set(build_details.remaining_problem_ids)
    assert not set(a_suite.problem_ids) & set(b_suite.problem_ids)
    assert build_details.suite_tier_counts().select("n_candidates_a", "n_candidates_db").rows() == [
        (32, 8),
        (16, 4),
        (16, 4),
    ]
    assert all_selection_details["sb-64a"].diversity > 0.0
    assert (all_selection_details["sb-64b"].tier_quotas, all_selection_details["sb-64b"].diversity) == (None, None)
    _check_quotas_and_nesting(build_details)


@pytest.mark.only_with_numba_jit
def test_each_series_nests_its_suites_and_the_stage_records_its_parameters():
    """A Core of 256 splits into 2 series of a suite of 128 and a suite of 64, each smaller suite inside the larger one
    of its series; each selection meets its own quotas, and the stage's parameters record max-div's time per candidate
    and seed."""
    # --- arrange ----------------------
    stage = DistillationStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    build_details = _distill({A: 64, B: 64, C: 64, DA: 40, DB: 24}, stage)

    # --- assert -----------------------
    all_selection_details = build_details.distilled_suite_selection_details()
    assert [(name, details.benchmark_suite.aliases) for name, details in all_selection_details.items()] == [
        ("sb-128a", ("sb-xsmall",)),
        ("sb-64a", ("sb-tiny",)),
        ("sb-128b", ()),
        ("sb-64b", ()),
    ]
    _check_quotas_and_nesting(build_details)
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}


def test_the_aliases_cover_each_a_series_size_of_the_largest_core():
    """The a-series of the largest Core holds 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to half the Core, and
    each such size has its aliases."""
    # --- arrange ----------------------
    a_series_sizes = set()
    size = SMALLEST_SUITE_SIZE
    while size <= max(CORE_SIZES) // 2:
        a_series_sizes.add(size)
        size *= 2

    # --- act / assert -----------------
    assert set(_PRIMARY_SERIES_ALIASES) == a_series_sizes
