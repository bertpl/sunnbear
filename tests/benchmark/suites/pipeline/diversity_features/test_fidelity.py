"""No `FeatureFidelity` member is an alias of another."""

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity


def test_no_fidelity_is_an_alias_and_each_value_starts_with_its_name():
    """No fidelity is an alias of another one, and the first part of each member's value is the member's name."""
    # --- act / assert -----------------
    assert len(FeatureFidelity) == len(FeatureFidelity.__members__)
    assert [fidelity.value[0] for fidelity in FeatureFidelity] == [fidelity.name for fidelity in FeatureFidelity]
