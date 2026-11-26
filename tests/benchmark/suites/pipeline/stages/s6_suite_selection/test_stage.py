"""`SuiteSelectionStage` selects the a-series and the b-series of benchmark suites from the candidates' fine features:

- the size of the largest suites is the largest that is at most half the number of candidates, and the stage stops the
  pipeline when the candidates are too few for 2 suites of the smallest size;
- it stores each candidate's tier, selects 2 disjoint largest suites, and drops the other candidates;
- where a tier has too few candidates for both largest suites, the largest suite of the b-series fills the rest of that
  tier's quota with candidates of a neighboring tier;
- each series' smaller suites lie inside its larger ones, and every suite meets the quotas that the stage stores for it;
- every suite's diversity score is the score of its own test problems;
- the stage records max-div's time per candidate and seed in its parameters;
- the a-series' aliases cover each of its sizes up to `MAX_SUITE_SIZE`.
"""

from collections import Counter
from itertools import pairwise

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierQuotas,
    compute_diversity_score,
)
from sunnbear._core.benchmark.suites.pipeline.stages import MAX_SUITE_SIZE, SMALLEST_SUITE_SIZE, SuiteSelectionStage
from sunnbear._core.benchmark.suites.pipeline.stages.s6_suite_selection.stage import _PRIMARY_SERIES_ALIASES
from sunnbear._core.benchmark.suites.pipeline.state import BenchmarkSuitesBuildDetails
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids

A, B, C, D = DifficultyTier

# The stage runs no tasks in the pool, so the pool's processes never start. max-div runs 1 worker per worker of the
# pool, and with 1 worker it warns that it gains nothing over a single solve, so the pool has 2 workers.
_TWO_WORKER_POOL = WorkerPool(n_workers=2)
# Each max-div worker runs this long per candidate of the selection's `CandidatePool`; with the pools of these tests,
# that covers the start of the workers' processes and leaves time to meet every constraint
# on a busy CI machine.
_SEC_PER_CANDIDATE = 0.03
# These are the ranges of each tier's EDIs, relative to `DEFAULT_N_BISECTION_FEVALS`; the EDIs differ within a tier,
# so that the distance between 2 EDIs of 1 tier is not 0.
_EDI_RATIO_RANGE_BY_TIER = {A: (0.1, 0.2), B: (0.3, 0.45), C: (0.6, 0.9), D: (1.2, 3.5)}


def _select_suites(tier_counts: dict[DifficultyTier, int], stage: SuiteSelectionStage) -> BenchmarkSuitesBuildDetails:
    """Run `stage` on `tier_counts` candidates of each tier, and return the build details of the run."""
    tiers = [tier for tier, count in tier_counts.items() for _ in range(count)]
    problem_ids = example_problem_ids(len(tiers))
    rng = np.random.default_rng(seed=4)
    edis = {
        problem_id: rng.uniform(*_EDI_RATIO_RANGE_BY_TIER[tier]) * DEFAULT_N_BISECTION_FEVALS
        for problem_id, tier in zip(problem_ids, tiers, strict=True)
    }
    state = build_state_before(PipelineStageId.SUITE_SELECTION, problem_ids, edis=edis)
    state.run_stage(stage, worker_pool=_TWO_WORKER_POOL)
    return state.create_build_details()


def _check_series_and_quotas(build_details: BenchmarkSuitesBuildDetails) -> None:
    """Check that the 2 series share no test problem, that each suite holds the next smaller one of its series, and
    that each suite meets its quotas.

    A test problem counts toward the tier whose recorded EDI range holds its EDI; the EDIs of `_select_suites` are all
    different, so the ranges do not overlap.
    """
    edis = build_details.edis(PipelineStageId.FINE_CHARACTERIZATION)
    all_selection_details = list(build_details.suite_selection_details().values())
    problem_ids_by_series = {"a": set(), "b": set()}
    for selection_details in all_selection_details:
        suite = selection_details.benchmark_suite
        problem_ids_by_series[suite.name[-1]] |= set(suite.problem_ids)
        tier_counts = {
            tier: sum(lower <= edis[p] <= upper for p in suite.problem_ids)
            for tier, (lower, upper) in selection_details.edi_range_by_tier.items()
        }
        assert tier_counts == DifficultyTierQuotas(len(suite.problem_ids)).quota_by_tier
    assert not problem_ids_by_series["a"] & problem_ids_by_series["b"]
    for selection_details, next_selection_details in pairwise(all_selection_details):
        suite, next_suite = selection_details.benchmark_suite, next_selection_details.benchmark_suite
        if suite.name[-1] == next_suite.name[-1]:
            assert set(next_suite.problem_ids) < set(suite.problem_ids)


@pytest.mark.parametrize(
    "n_candidates, largest_suite_size_expected",
    [
        pytest.param(128, 64, id="smallest"),
        pytest.param(300, 128, id="between_sizes"),
        pytest.param(2047, 512, id="just_below_2_suites_of_1024"),
        pytest.param(9999, 1024, id="capped_at_1024"),
    ],
)
def test_the_largest_suite_size_is_the_largest_that_the_candidates_fill_twice(
    n_candidates, largest_suite_size_expected
):
    """The size of the largest suites is the largest power of 2 up to `MAX_SUITE_SIZE` of which the candidates fill 2
    suites."""
    # --- act / assert -----------------
    assert SuiteSelectionStage._choose_largest_suite_size(n_candidates) == largest_suite_size_expected


def test_the_stage_stops_the_pipeline_below_2_suites_of_the_smallest_size():
    """The stage stops the pipeline for 127 candidates, fewer than 2 suites of 64 need, and the message gives the
    127."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(127)
    state = build_state_before(PipelineStageId.SUITE_SELECTION, problem_ids, edis=dict.fromkeys(problem_ids, 5.0))

    # --- act / assert -----------------
    with pytest.raises(
        PipelineStopError,
        match=r"^There are 127 candidates, fewer than the 128 that 2 benchmark suites of 64 test problems need\.$",
    ):
        state.run_stage(SuiteSelectionStage(_SEC_PER_CANDIDATE), worker_pool=_TWO_WORKER_POOL)


@pytest.mark.only_with_numba_jit
def test_the_stage_selects_2_disjoint_largest_suites_and_drops_the_other_candidates():
    """Of 160 candidates, 40 of each tier, the stage selects `sb-64a`, alias `sb-tiny`, and `sb-64b`, each with 16 of
    each tier, and drops the other 32 with the reason `not_in_any_suite`; each suite's diversity score is that of
    its own 64 test problems."""
    # --- act --------------------------
    build_details = _select_suites({A: 40, B: 40, C: 40, D: 40}, SuiteSelectionStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    all_selection_details = build_details.suite_selection_details()
    assert [(name, details.benchmark_suite.aliases) for name, details in all_selection_details.items()] == [
        ("sb-64a", ("sb-tiny",)),
        ("sb-64b", ()),
    ]
    assert len(build_details.difficulty_tiers()) == 160
    drops = [build_details.drop_of(problem_id) for problem_id in build_details.problem_ids]
    assert Counter(drop.reason for drop in drops if drop is not None) == {"not_in_any_suite": 32}
    assert build_details.suite_tier_counts().select("n_candidates_a", "n_candidates_d").rows() == [(16, 16), (16, 16)]
    results = build_details.characterization_results(PipelineStageId.FINE_CHARACTERIZATION)
    for selection_details in all_selection_details.values():
        suite_pool = CandidatePool.from_feature_matrix(
            results.build_scaled_feature_matrix(selection_details.benchmark_suite.problem_ids),
            edis=results.edis,
            n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
        )
        assert selection_details.diversity == compute_diversity_score(suite_pool) > 0.0
    _check_series_and_quotas(build_details)


@pytest.mark.only_with_numba_jit
def test_the_b_series_carries_a_shortage_and_the_stage_records_its_parameters():
    """Only 24 candidates are of tier D: `sb-64a` takes 16 of them, so `sb-64b` holds the other 8, and 8 candidates of
    C with the highest EDIs count toward its quota of D; the stage's parameters record max-div's time per candidate and
    seed."""
    # --- arrange ----------------------
    stage = SuiteSelectionStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    build_details = _select_suites({A: 40, B: 40, C: 56, D: 24}, stage)

    # --- assert -----------------------
    assert build_details.suite_tier_counts().select(
        "n_candidates_a", "n_candidates_b", "n_candidates_c", "n_candidates_d"
    ).rows() == [(16, 16, 16, 16), (16, 16, 24, 8)]
    b_suite_edi_range_of_d = build_details.suite_selection_details()["sb-64b"].edi_range_by_tier[D]
    assert b_suite_edi_range_of_d[0] < D.edi_range(DEFAULT_N_BISECTION_FEVALS)[0]
    _check_series_and_quotas(build_details)
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}


@pytest.mark.only_with_numba_jit
def test_each_series_nests_its_suites():
    """256 candidates fill 2 series of a suite of 128 and a suite of 64, each smaller suite inside the larger one of
    its series, and each suite meets its own quotas."""
    # --- act --------------------------
    build_details = _select_suites({A: 64, B: 64, C: 64, D: 64}, SuiteSelectionStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    all_selection_details = build_details.suite_selection_details()
    assert [(name, details.benchmark_suite.aliases) for name, details in all_selection_details.items()] == [
        ("sb-128a", ("sb-xsmall",)),
        ("sb-64a", ("sb-tiny",)),
        ("sb-128b", ()),
        ("sb-64b", ()),
    ]
    _check_series_and_quotas(build_details)


def test_the_aliases_cover_each_a_series_size_up_to_the_max_suite_size():
    """The a-series of a run whose largest suites have `MAX_SUITE_SIZE` holds 1 suite per power of 2 from
    `SMALLEST_SUITE_SIZE` up to `MAX_SUITE_SIZE`, and each such size has its aliases."""
    # --- arrange ----------------------
    a_series_sizes = set()
    size = SMALLEST_SUITE_SIZE
    while size <= MAX_SUITE_SIZE:
        a_series_sizes.add(size)
        size *= 2

    # --- act / assert -----------------
    assert set(_PRIMARY_SERIES_ALIASES) == a_series_sizes
