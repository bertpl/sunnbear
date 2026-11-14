"""Every `FeatureFidelity` is a member of its own, and gives the tuples of its snuffled analyses."""

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity


def test_every_fidelity_is_a_member_of_its_own_whose_value_starts_with_its_name():
    """No fidelity is an alias of another one, and the first part of each member's value is the member's name."""
    assert len(FeatureFidelity) == len(FeatureFidelity.__members__)
    assert [fidelity.value[0] for fidelity in FeatureFidelity] == [fidelity.name for fidelity in FeatureFidelity]


@pytest.mark.parametrize("fidelity", FeatureFidelity)
def test_snuffled_mc_tuples_are_the_first_tuples_of_the_shipped_set(fidelity):
    """The tuples of a fidelity's snuffled analyses are the first `n_snuffled_analyses` tuples of the shipped set."""
    # --- act --------------------------
    tuples = fidelity.snuffled_mc_tuples

    # --- assert -----------------------
    full = load_mc_tuples(max(MCTuplesSize))
    assert tuples.u.tolist() == full.u[: fidelity.n_snuffled_analyses].tolist()
    assert tuples.v.tolist() == full.v[: fidelity.n_snuffled_analyses].tolist()
