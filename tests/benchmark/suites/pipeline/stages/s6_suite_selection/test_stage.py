"""`SuiteSelectionStage` selects the built-in series of benchmark suites from the candidates' fine features:

- the size of the largest suites of disjoint series is the largest at which their suites fit into the candidates, and
  the stage stops the pipeline when the candidates are too few for 2 suites of the smallest size of the a-series and
  the b-series;
- it stores each candidate's tier, selects 2 disjoint largest suites of the a-series and the b-series, and drops the
  other candidates;
- the pub-series selects its suites from the candidates of category 1 alone, and the stage does not drop the
  candidates of its largest suite;
- where a tier has too few candidates for both largest suites, the largest suite of the b-series misses that tier's
  quota, and its selection details record that the suite misses the quota;
- each series' smaller suites lie inside its larger ones, and every suite meets its quotas when the candidates allow;
- every suite carries the id of its series, and the name and aliases that its series gives it;
- every suite's diversity score is the score of its own test problems;
- the stage records max-div's time per candidate and seed in its parameters;
- the stage declares 1 selection spec per built-in series, in the order of the series.
"""

from collections import Counter
from itertools import pairwise

import numpy as np
import polars as pl
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS
from sunnbear._core.benchmark.suites.benchmark_suite import BUILT_IN_SERIES, PUB_SERIES, SB_A_SERIES, SB_B_SERIES
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    QuotaFulfillment,
    compute_diversity_score,
)
from sunnbear._core.benchmark.suites.pipeline.stages import SuiteSelectionStage
from sunnbear._core.benchmark.suites.pipeline.stages.s6_suite_selection.stage import _SERIES_SELECTION_SPECS
from sunnbear._core.benchmark.suites.pipeline.state import BenchmarkSuitesBuildDetails
from sunnbear._core.problems.catalog.c01_published_test_problems import PublishedTestProblems
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


def _select_suites(
    tier_counts: dict[DifficultyTier, int],
    stage: SuiteSelectionStage,
    *,
    published_tier_counts: dict[DifficultyTier, int] | None = None,
) -> BenchmarkSuitesBuildDetails:
    """Run `stage` on `tier_counts` candidates of each tier, and `published_tier_counts` more of category 1, and return
    the build details of the run.

    The candidates of category 1 are of formula 1.900, which no catalog holds; the others are of formula 99.1.
    """
    tiers = [tier for tier, count in tier_counts.items() for _ in range(count)]
    published_tiers = [tier for tier, count in (published_tier_counts or {}).items() for _ in range(count)]
    problem_ids = example_problem_ids(len(tiers)) + example_problem_ids(
        len(published_tiers), category_number=1, formula_number=900
    )
    tiers += published_tiers
    rng = np.random.default_rng(seed=4)
    edis = {
        problem_id: rng.uniform(*_EDI_RATIO_RANGE_BY_TIER[tier]) * DEFAULT_N_BISECTION_FEVALS
        for problem_id, tier in zip(problem_ids, tiers, strict=True)
    }
    state = build_state_before(PipelineStageId.SUITE_SELECTION, problem_ids, edis=edis)
    state.run_stage(stage, worker_pool=_TWO_WORKER_POOL)
    return state.create_build_details()


def _check_series_and_quotas(build_details: BenchmarkSuitesBuildDetails, *, is_every_quota_met: bool = True) -> None:
    """Check the suites of every series, and that each suite holds the next smaller one of its series:

    - the a-series and the b-series share no test problem, and each of their suites records a quota of a quarter per
      tier, which counts the suite's test problems of that tier;
    - each suite of the pub-series holds only candidates of category 1, and records no quota.

    With `is_every_quota_met`, also check that every suite meets every quota.
    """
    difficulty_tiers = build_details.difficulty_tiers()
    all_selection_details = list(build_details.suite_selection_details().values())
    problem_ids_by_series_id = {series.series_id: set() for series in BUILT_IN_SERIES}
    for selection_details in all_selection_details:
        suite = selection_details.benchmark_suite
        problem_ids_by_series_id[suite.series_id] |= set(suite.problem_ids)
        if suite.series_id == PUB_SERIES.series_id:
            assert selection_details.quota_fulfillments == ()
            assert all(
                PublishedTestProblems.is_ancestor_of(problem_id.formula_number) for problem_id in suite.problem_ids
            )
        else:
            tier_counts = Counter(difficulty_tiers[problem_id] for problem_id in suite.problem_ids)
            quota_count = len(suite.problem_ids) // 4
            assert selection_details.quota_fulfillments == tuple(
                QuotaFulfillment(
                    group_label=tier.value,
                    min_count=quota_count,
                    max_count=quota_count,
                    n_selected_in_group=tier_counts[tier],
                )
                for tier in DifficultyTier
            )
            if is_every_quota_met:
                assert all(tier_counts[tier] == quota_count for tier in DifficultyTier)
    assert not problem_ids_by_series_id[SB_A_SERIES.series_id] & problem_ids_by_series_id[SB_B_SERIES.series_id]
    for selection_details, next_selection_details in pairwise(all_selection_details):
        suite, next_suite = selection_details.benchmark_suite, next_selection_details.benchmark_suite
        if suite.series_id == next_suite.series_id:
            assert set(next_suite.problem_ids) < set(suite.problem_ids)


@pytest.mark.parametrize(
    "disjoint_series, n_candidates, largest_suite_size_expected",
    [
        pytest.param((SB_A_SERIES, SB_B_SERIES), 127, None, id="sb_too_few"),
        pytest.param((SB_A_SERIES, SB_B_SERIES), 128, 64, id="sb_smallest"),
        pytest.param((SB_A_SERIES, SB_B_SERIES), 300, 128, id="sb_between_sizes"),
        pytest.param((SB_A_SERIES, SB_B_SERIES), 2047, 512, id="sb_just_below_2_suites_of_1024"),
        pytest.param((SB_A_SERIES, SB_B_SERIES), 9999, 1024, id="sb_capped_at_1024"),
        pytest.param((PUB_SERIES,), 63, None, id="pub_too_few"),
        pytest.param((PUB_SERIES,), 64, 64, id="pub_smallest"),
        pytest.param((PUB_SERIES,), 1007, 512, id="pub_capped_at_512"),
    ],
)
def test_the_largest_suite_size_is_the_largest_at_which_the_disjoint_suites_fit(
    disjoint_series, n_candidates, largest_suite_size_expected
):
    """The size of the largest suites of disjoint series is the largest size that each of them declares and at which
    1 suite per series fits into the candidates, or None when not even the smallest size fits."""
    # --- act / assert -----------------
    assert (
        SuiteSelectionStage._choose_largest_suite_size(n_candidates, disjoint_series=disjoint_series)
        == largest_suite_size_expected
    )


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
    """Of 160 candidates, 40 of each tier, the stage selects `sb-64a` of the a-series, alias `sb-tiny`, and `sb-64b` of
    the b-series, each with 16 of each tier, and drops the other 32 with the reason `not_in_any_suite`; each suite's
    diversity score is that of its own 64 test problems."""
    # --- act --------------------------
    build_details = _select_suites({A: 40, B: 40, C: 40, D: 40}, SuiteSelectionStage(_SEC_PER_CANDIDATE))

    # --- assert -----------------------
    all_selection_details = build_details.suite_selection_details()
    assert [
        (name, details.benchmark_suite.series_id, details.benchmark_suite.aliases)
        for name, details in all_selection_details.items()
    ] == [("sb-64a", "sb-a", ("sb-tiny",)), ("sb-64b", "sb-b", ())]
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
    """Only 24 candidates are of tier D: `sb-64a` takes 16 of them and meets its quotas, so `sb-64b` holds the other 8
    and misses its quota of D, which its selection details record; the stage's parameters record max-div's time per
    candidate and seed."""
    # --- arrange ----------------------
    stage = SuiteSelectionStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    build_details = _select_suites({A: 40, B: 40, C: 56, D: 24}, stage)

    # --- assert -----------------------
    all_selection_details = build_details.suite_selection_details()
    assert all(f.n_selected_in_group == f.min_count for f in all_selection_details["sb-64a"].quota_fulfillments)
    b_suite_tier_counts = build_details.suite_tier_counts().filter(pl.col("suite_name") == "sb-64b")
    assert b_suite_tier_counts.select("n_candidates_d").item() == 8
    assert all(b_suite_tier_counts.select(f"n_candidates_{tier.lower()}").item() >= 16 for tier in "ABC")
    _check_series_and_quotas(build_details, is_every_quota_met=False)
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


@pytest.mark.only_with_numba_jit
def test_the_pub_series_nests_suites_of_category_1_and_the_drops_keep_its_candidates():
    """Of 160 candidates, 140 of category 1, the stage selects `sb-64a` and `sb-64b`, and `pub-128` and `pub-64` from
    the 140 alone; it drops only the candidates that none of `sb-64a`, `sb-64b` and `pub-128` holds."""
    # --- act --------------------------
    build_details = _select_suites(
        {A: 5, B: 5, C: 5, D: 5},
        SuiteSelectionStage(_SEC_PER_CANDIDATE),
        published_tier_counts={A: 35, B: 35, C: 35, D: 35},
    )

    # --- assert -----------------------
    all_selection_details = build_details.suite_selection_details()
    assert list(all_selection_details) == ["sb-64a", "sb-64b", "pub-128", "pub-64"]
    kept_problem_id_set = {
        problem_id
        for name in ("sb-64a", "sb-64b", "pub-128")
        for problem_id in all_selection_details[name].benchmark_suite.problem_ids
    }
    drops = [build_details.drop_of(problem_id) for problem_id in build_details.problem_ids]
    assert Counter(drop.reason for drop in drops if drop is not None) == {
        "not_in_any_suite": 160 - len(kept_problem_id_set)
    }
    _check_series_and_quotas(build_details)


def test_the_stage_declares_a_selection_spec_per_built_in_series():
    """`_SERIES_SELECTION_SPECS` holds 1 spec per built-in series, in the order of `BUILT_IN_SERIES`."""
    # --- act / assert -----------------
    assert tuple(spec.series for spec in _SERIES_SELECTION_SPECS) == BUILT_IN_SERIES
