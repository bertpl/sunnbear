"""`DifficultyTierQuotas` gives each tier its share of the selection, refuses a size without whole quotas, and checks
that a selection meets each quota."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier, DifficultyTierQuotas

A, B, C, DA, DB = DifficultyTier


def test_each_tier_has_its_share_of_the_selection():
    """A selection of 128 has quotas of 32 each for A, B and C, 24 for Da and 8 for Db."""
    # --- act / assert -----------------
    assert DifficultyTierQuotas(128).quota_by_tier == {A: 32, B: 32, C: 32, DA: 24, DB: 8}


@pytest.mark.parametrize("selection_size", [0, 100])
def test_quotas_are_refused_for_a_size_without_positive_whole_quotas(selection_size):
    """A size that is not a positive multiple of 16 gives Db a quota that is not a positive whole number."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=f"A selection of {selection_size} candidates gives some tier a quota"):
        DifficultyTierQuotas(selection_size)


@pytest.mark.parametrize(
    "selected_tiers, message",
    [
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 24 + [DB] * 8, None, id="met"),
        pytest.param(
            [A] * 33 + [B] * 31 + [C] * 32 + [DA] * 24 + [DB] * 8,
            r"128 candidates .* A: 33 of 32; B: 31 of 32\.$",
            id="unmet",
        ),
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 24, r"120 candidates .* Db: 0 of 8\.$", id="few"),
    ],
)
def test_a_selection_must_meet_every_quota(selected_tiers, message):
    """A selection that meets every quota passes; one that misses a quota stops the pipeline, with a message that names
    each unmet quota and the number of selected candidates of its tier."""
    # --- arrange ----------------------
    quotas = DifficultyTierQuotas(128)

    # --- act / assert -----------------
    if message is None:
        quotas.check_selection(selected_tiers)
    else:
        with pytest.raises(PipelineStopError, match=message):
            quotas.check_selection(selected_tiers)
