"""`map_fevals_to_feature` maps evaluation counts from [2, max_fevals] onto [0, 1], and `map_feature_to_fevals` maps
them back."""

import numpy as np

from sunnbear._core.benchmark.suites.pipeline.features import map_feature_to_fevals, map_fevals_to_feature


def test_the_mapping_sends_2_and_max_fevals_to_0_and_1_and_inverts():
    """The counts 2 and 160 map to 0 and 1, the geometric midpoint 2 * sqrt(80) to 0.5, and each count maps back."""
    # --- arrange ----------------------
    n_fevals = np.array([2.0, 2.0 * np.sqrt(80.0), 13.0, 160.0])

    # --- act --------------------------
    features = map_fevals_to_feature(n_fevals, max_fevals=160)

    # --- assert -----------------------
    np.testing.assert_allclose(features[[0, 1, 3]], [0.0, 0.5, 1.0], atol=1e-15)
    np.testing.assert_allclose(map_feature_to_fevals(features, max_fevals=160), n_fevals, rtol=1e-14)
