"""`select_diverse_problem_ids` stops the pipeline when max-div's selection misses a quota, and its distance over the
feature columns is the L1 distance that leaves the EDI column out."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierQuotas,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection import l1_distance_over_leading_columns
from sunnbear._core.stats import l1_distances_to
from tests.benchmark.suites.pipeline.example_states import example_problem_ids


@pytest.mark.only_with_numba_jit
def test_a_selection_that_misses_a_quota_stops_the_pipeline():
    """Quotas whose 2 groups both hold tier A ask for 8 candidates of A, and for 4 of A and B together, so no
    selection meets both; max-div returns its best selection, and the check after max-div's selection stops the
    pipeline."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=5)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(example_problem_ids(40)), values=rng.random((40, 4))),
        edis=rng.uniform(2, 160, size=40),
        difficulty_tiers=(DifficultyTier.A,) * 30 + (DifficultyTier.B,) * 10,
    )
    tier_quotas = DifficultyTierQuotas(
        quota_by_group={frozenset({DifficultyTier.A}): 8, frozenset({DifficultyTier.A, DifficultyTier.B}): 4}
    )

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"unmet quotas: .*A and B: \d+ of 4"):
        select_diverse_problem_ids(pool, tier_quotas=tier_quotas, seed=1, sec_per_candidate=0.05, n_workers=2)


def test_the_feature_distance_is_the_l1_distance_over_the_leading_columns():
    """Over the first 4 of 5 columns, the distance equals the L1 distance between the vectors without their last
    column."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=6)
    a, b = rng.random(5).astype(np.float32), rng.random(5).astype(np.float32)

    # --- act --------------------------
    distance = l1_distance_over_leading_columns(a, b, 4)

    # --- assert -----------------------
    assert distance == pytest.approx(l1_distances_to(a[np.newaxis, :4], b[:4])[0], rel=1e-6)
