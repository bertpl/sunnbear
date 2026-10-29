"""`FeatureFidelity.feature_column_names` names the solvers block first, then the snuffled block, and starts each column
with its block's prefix; no feature scale column starts with such a prefix, and `FeatureFidelity.add_feature_scales`
adds each block's mean pairwise L1 distance."""

import numpy as np
import polars as pl
import polars.selectors as cs
from snuffled import FunctionProperty, RootProperty

from sunnbear._core.benchmark.suites.pipeline.features import SNUFFLED_PROPERTIES, FeatureBlock, FeatureFidelity
from sunnbear._core.stats import mean_pairwise_l1


def test_the_column_names_hold_1_geomean_per_config_9_gpq_levels_and_10_properties():
    """For 2 configs, the names are the 2 geomeans in their order, the gpq levels 10 to 90, then snuffled's 10
    properties."""
    # --- act --------------------------
    column_names = FeatureFidelity.COARSE.feature_column_names(["brent", "toms748[k=1]"])

    # --- assert -----------------------
    assert column_names == [
        "coarse_solvers_geomean_brent",
        "coarse_solvers_geomean_toms748[k=1]",
        *(f"coarse_solvers_gpq_{level}" for level in range(10, 100, 10)),
        *(f"coarse_snuffled_{prop.value}" for prop in SNUFFLED_PROPERTIES),
    ]
    assert set(SNUFFLED_PROPERTIES) == {*RootProperty, *FunctionProperty}


def test_the_scale_columns_are_not_selected_as_feature_columns():
    """Every feature column starts with its block's prefix, and no column of a block's scale does."""
    # --- arrange ----------------------
    fidelity = FeatureFidelity.COARSE
    prefixes = [fidelity.feature_column_prefix(block) for block in FeatureBlock]

    # --- act --------------------------
    scale_column_names = fidelity.feature_scale_column_names()

    # --- assert -----------------------
    assert prefixes == ["coarse_solvers_", "coarse_snuffled_"]
    assert scale_column_names == ["coarse_feature_scale_solvers", "coarse_feature_scale_snuffled"]
    assert all(column_name.startswith(tuple(prefixes)) for column_name in fidelity.feature_column_names(["brent"]))
    assert not any(column_name.startswith(tuple(prefixes)) for column_name in scale_column_names)


def test_each_blocks_scale_is_its_mean_pairwise_l1_distance_in_every_row():
    """The scale of a block is the mean pairwise L1 distance over the columns of that block only."""
    # --- arrange ----------------------
    fidelity = FeatureFidelity.COARSE
    rng = np.random.default_rng(seed=1)
    table = pl.DataFrame(
        {
            "problem_id": [f"f99.{idx}" for idx in range(5)],
            **{column_name: rng.random(5) for column_name in fidelity.feature_column_names(["brent", "illinois"])},
        }
    )

    # --- act --------------------------
    table_with_scales = fidelity.add_feature_scales(table)

    # --- assert -----------------------
    assert table_with_scales.select(table.columns).equals(table)
    for block in FeatureBlock:
        scale_expected = mean_pairwise_l1(
            table.select(cs.starts_with(fidelity.feature_column_prefix(block))).to_numpy()
        )
        assert table_with_scales[fidelity.feature_scale_column_name(block)].to_list() == [scale_expected] * 5
