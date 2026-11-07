"""`map_fevals_to_feature` maps evaluation counts from [2, max_fevals] onto [0, 1] on a log scale."""

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.diversity_features import map_fevals_to_feature


def test_the_mapping_sends_2_and_max_fevals_to_0_and_1():
    """The counts 2 and 160 map to 0 and 1, and the geometric midpoint 2 * sqrt(80) to 0.5."""
    # --- act --------------------------
    features = map_fevals_to_feature([2.0, 2.0 * np.sqrt(80.0), 160.0], max_fevals=160)

    # --- assert -----------------------
    np.testing.assert_allclose(features, [0.0, 0.5, 1.0], atol=1e-15)
