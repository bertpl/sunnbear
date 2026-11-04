"""`compute_edi` returns the geometric mean of the evaluation counts of all solves together."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import compute_edi


def test_the_edi_is_the_geometric_mean_of_all_solves():
    """Solves of 2 configs, at 2 and 8 and at 8 and 32 evaluations, have an EDI of 8."""
    # --- act / assert -----------------
    assert compute_edi(np.array([[2.0, 8.0], [8.0, 32.0]])) == pytest.approx(8.0)
