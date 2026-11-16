"""`select_diverse_problem_ids` stops the pipeline when max-div's selection misses a quota, and its distance over the
feature columns is the L1 distance that leaves the EDI column out."""

from types import SimpleNamespace

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTierAssignment,
    DifficultyTierQuotas,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection import l1_distance_over_leading_columns
from sunnbear._core.stats import l1_distances_to
from tests.benchmark.suites.pipeline.example_states import example_problem_ids


class _FirstCandidatesSolverBuilder:
    """`_FirstCandidatesSolverBuilder` stands in for max-div's solver builder, and selects the first k candidates."""

    def __init__(self, max_div_problem: object) -> None:
        """Keep the problem, whose `k` sets the number of candidates to select."""
        self.max_div_problem = max_div_problem

    def with_seed(self, seed: int) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which ignores the seed."""
        return self

    def with_workers(self, duration: object, n_workers: int) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which ignores the time and the workers."""
        return self

    def build(self) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which also acts as its solver."""
        return self

    def solve(self, verbosity: object) -> SimpleNamespace:
        """Return a solution that selects the first k candidates, with a diversity score of 1."""
        return SimpleNamespace(i_selected=list(range(self.max_div_problem.k)), score=SimpleNamespace(diversity=1.0))


def test_a_selection_that_misses_a_quota_stops_the_pipeline(monkeypatch):
    """max-div treats its constraints as soft; a stand-in for its solver selects the first 16 of 32 candidates, all of
    tier A, so the check after the selection stops the pipeline."""
    # --- arrange ----------------------
    monkeypatch.setattr(
        "sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection.ParallelMaxDivSolverBuilder",
        _FirstCandidatesSolverBuilder,
    )
    rng = np.random.default_rng(seed=5)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(example_problem_ids(32)), values=rng.random((32, 4))),
        edis=np.array([5.0] * 16 + [15.0] * 4 + [30.0] * 4 + [60.0] * 4 + [120.0] * 4),
        n_bisection_fevals=40,
    )
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(16))

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"unmet quotas: A: 16 of 4; B: 0 of 4; C: 0 of 4; Da: 0 of 3; Db: 0"):
        select_diverse_problem_ids(pool, tier_assignment=tier_assignment, seed=1, sec_per_candidate=0.05, n_workers=2)


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
