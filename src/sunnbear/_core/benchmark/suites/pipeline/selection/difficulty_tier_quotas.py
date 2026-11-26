"""`DifficultyTierQuotas` holds the quotas of 1 selection: how many selected candidates count toward each tier."""

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError

from .difficulty_tier import DifficultyTier


# ==================================================================================================
#  DifficultyTierQuotas
# ==================================================================================================
@dataclass(frozen=True)
class DifficultyTierQuotas:
    """A `DifficultyTierQuotas` gives each tier the exact number of the selected candidates that count toward it.

    Each tier's quota is `selection_size` times the tier's `quota_share`. The candidates that count toward a tier are
    those with that assigned tier, which `DifficultyTierAssignment` gives.

    Attributes:
        selection_size: The number of the selected candidates that count toward the quotas, which leaves out any
            required candidates; a positive multiple of the denominator of every tier's `quota_share`, so that every
            tier's quota is whole and at least 1.
    """

    selection_size: int

    def __post_init__(self) -> None:
        """Refuse a selection size that gives some tier a quota that is not a positive whole number.

        Raises:
            ValueError: If `selection_size` is not a positive multiple of the denominator of every tier's
                `quota_share`.
        """
        size_divisor = math.lcm(*(tier.quota_share.denominator for tier in DifficultyTier))
        if self.selection_size <= 0 or self.selection_size % size_divisor != 0:
            raise ValueError(
                f"A selection of {self.selection_size} candidates gives some tier a quota that is not a positive "
                f"whole number; a selection's size must be a positive multiple of {size_divisor}."
            )

    @property
    def quota_by_tier(self) -> dict[DifficultyTier, int]:
        """Return each tier's quota, in the order of `DifficultyTier`."""
        return {tier: int(self.selection_size * tier.quota_share) for tier in DifficultyTier}

    def check_selection(self, selected_assigned_tiers: Sequence[DifficultyTier]) -> None:
        """Stop the pipeline unless the selected candidates, given by their assigned tiers, meet every quota exactly.

        The quotas sum to `selection_size`, so a selection that meets every quota also has that size.

        Raises:
            PipelineStopError: If `selected_assigned_tiers` does not meet a quota exactly; the message names each such
                tier with the number of selected candidates that count toward it.
        """
        tier_counts = Counter(selected_assigned_tiers)
        unmet_quota_descriptions = [
            f"{tier.value}: {tier_counts[tier]} of {quota}"
            for tier, quota in self.quota_by_tier.items()
            if tier_counts[tier] != quota
        ]
        if unmet_quota_descriptions:
            raise PipelineStopError(
                f"The selection holds {len(selected_assigned_tiers)} candidates for a selection of "
                f"{self.selection_size}; unmet quotas: {'; '.join(unmet_quota_descriptions)}."
            )
