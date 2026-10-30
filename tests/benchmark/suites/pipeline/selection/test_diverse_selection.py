"""`select_diverse_suite` stops the pipeline when max-div's selection misses a quota of the suite."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DifficultyClass,
    DifficultyQuota,
    SuiteComposition,
    select_diverse_suite,
)


@pytest.mark.only_with_numba_jit
def test_a_selection_that_misses_a_quota_stops_the_pipeline():
    """A composition whose 2 quotas both count class A asks for 8 candidates of A, and for 4 of A and B together, so no
    selection meets both; max-div returns its best selection, and the check after it stops the pipeline."""
    # --- arrange ----------------------
    vectors = np.random.default_rng(seed=5).random((40, 4))
    composition = SuiteComposition(
        quotas=(
            DifficultyQuota(classes=frozenset({DifficultyClass.A}), count=8),
            DifficultyQuota(classes=frozenset({DifficultyClass.A, DifficultyClass.B}), count=4),
        )
    )

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"unmet quotas: .*A and B: \d+ of 4"):
        select_diverse_suite(
            vectors,
            edi_axis=0,
            difficulty_classes=[DifficultyClass.A] * 30 + [DifficultyClass.B] * 10,
            composition=composition,
            seed=1,
            sec_per_candidate=0.05,
            n_workers=2,
        )
