"""`FeatureFidelity.feature_column_names` names the solvers block first, then the snuffled block, each with the
fidelity's prefix."""

from snuffled import FunctionProperty, RootProperty

from sunnbear._core.benchmark.suites.pipeline.features import SNUFFLED_PROPERTIES, FeatureFidelity


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
