"""`select_diverse_suite` stops the pipeline when max-div's selection misses a quota of the suite, and its distance over
the feature columns is the L1 distance that leaves the EDI column out."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyClass,
    DifficultyQuota,
    SuiteComposition,
    select_diverse_suite,
)
from sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection import l1_distance_over_leading_columns
from sunnbear._core.stats import l1_distances_to
from tests.benchmark.suites.pipeline.example_states import example_problem_ids


@pytest.mark.only_with_numba_jit
def test_a_selection_that_misses_a_quota_stops_the_pipeline():
    """A composition whose 2 quotas both count class A asks for 8 candidates of A, and for 4 of A and B together, so no
    selection meets both; max-div returns its best selection, and the check after max-div's selection stops the
    pipeline."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=5)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(example_problem_ids(40)), values=rng.random((40, 4))),
        edis=rng.uniform(2, 160, size=40),
        difficulty_classes=(DifficultyClass.A,) * 30 + (DifficultyClass.B,) * 10,
    )
    composition = SuiteComposition(
        quotas=(
            DifficultyQuota(classes=frozenset({DifficultyClass.A}), count=8),
            DifficultyQuota(classes=frozenset({DifficultyClass.A, DifficultyClass.B}), count=4),
        )
    )

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"unmet quotas: .*A and B: \d+ of 4"):
        select_diverse_suite(pool, composition=composition, seed=1, sec_per_candidate=0.05, n_workers=2)


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
