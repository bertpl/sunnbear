"""`DifficultyTierQuotas` holds the quotas of 1 selection: how many selected candidates each group of tiers holds.

`DifficultyTierQuotas.resolve` chooses the quotas of a selection from its size and the candidates that it selects from,
so that every quota can be met.
"""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Self

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError

from .difficulty_tier import DifficultyTier


# ==================================================================================================
#  DifficultyTierQuotas
# ==================================================================================================
@dataclass(frozen=True)
class DifficultyTierQuotas:
    """A `DifficultyTierQuotas` maps each group of tiers to the exact number of the selected candidates in that group.

    A group holds 1 tier, or several tiers that are next to each other in the order of `DifficultyTier` and share 1
    quota. A group that holds every tier imposes no constraint on the selection.

    Attributes:
        counts: The quota of each group, in the order of `DifficultyTier`.
    """

    counts: Mapping[frozenset[DifficultyTier], int]

    @property
    def size(self) -> int:
        """Return the number of candidates of the selection: the sum of the quotas."""
        return sum(self.counts.values())

    def check_selection(self, selected_tiers: Sequence[DifficultyTier]) -> None:
        """Stop the pipeline unless a selection of candidates, given by their tiers, has the size and meets each quota.

        Raises:
            PipelineStopError: If `selected_tiers` does not hold `size` candidates, or does not meet a quota exactly;
                the message names each such quota with the selection's count.
        """
        tier_counts = Counter(selected_tiers)
        unmet_quota_descriptions = [
            f"{self._describe_group(tiers)}: {sum(tier_counts[tier] for tier in tiers)} of {count}"
            for tiers, count in self.counts.items()
            if sum(tier_counts[tier] for tier in tiers) != count
        ]
        if len(selected_tiers) != self.size or unmet_quota_descriptions:
            raise PipelineStopError(
                f"The selection holds {len(selected_tiers)} candidates for a selection of {self.size}; unmet quotas: "
                f"{'; '.join(unmet_quota_descriptions) or 'none'}."
            )

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_json_values(self) -> list[dict[str, Any]]:
        """Return the quotas as JSON values: 1 item per group, with its ``tiers`` and its ``count``."""
        return [
            {"tiers": [tier.value for tier in DifficultyTier if tier in tiers], "count": count}
            for tiers, count in self.counts.items()
        ]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _describe_group(tiers: frozenset[DifficultyTier]) -> str:
        """Return the names of the tiers of a group, in the order of `DifficultyTier`, joined by "and"."""
        return " and ".join(tier.value for tier in DifficultyTier if tier in tiers)

    @staticmethod
    def _quota_of(group: frozenset[DifficultyTier], size: int) -> int:
        """Return the quota of `group` in a selection of `size`: `size` times the sum of its tiers' `core_share`."""
        return int(size * sum((tier.core_share for tier in group), start=Fraction(0)))

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def resolve(cls, size: int, pool_tier_counts: Mapping[DifficultyTier, int]) -> Self:
        """Return the quotas of a selection of `size` candidates, merged until the candidates can meet every quota.

        The quotas start at 1 per tier, of `size` times the tier's `core_share`. While a quota asks for more
        candidates than its group holds, the quota with the largest shortfall merges with its neighbor in the order of
        `DifficultyTier` whose quota is smaller; between 2 neighbors with equal quotas, it merges with the higher tier.
        At worst, 1 group holds every tier.

        Args:
            size: The number of candidates to select; a multiple of 16, so that every tier's quota is whole.
            pool_tier_counts: The number of candidates of each tier to select from; a missing tier has none.

        Raises:
            ValueError: If `size` is not a multiple of 16, or the candidates to select from number fewer than `size`.
        """
        if size % 16 != 0:
            raise ValueError(f"A selection of {size} candidates gives some tier a quota that is not whole.")
        elif sum(pool_tier_counts.values()) < size:
            raise ValueError(f"{sum(pool_tier_counts.values())} candidates cannot fill a selection of {size}.")
        else:
            groups = [frozenset({tier}) for tier in DifficultyTier]
            while True:
                shortfalls = [
                    cls._quota_of(group, size) - sum(pool_tier_counts.get(tier, 0) for tier in group)
                    for group in groups
                ]
                group_idx = shortfalls.index(max(shortfalls))
                if shortfalls[group_idx] <= 0:
                    return cls(counts={group: cls._quota_of(group, size) for group in groups})
                else:
                    # Of the 2 neighbors, the one with the smaller quota; on a tie, the higher one, which comes later.
                    neighbor_idx = min(
                        (idx for idx in (group_idx - 1, group_idx + 1) if 0 <= idx < len(groups)),
                        key=lambda idx: (cls._quota_of(groups[idx], size), -idx),
                    )
                    first_idx = min(group_idx, neighbor_idx)
                    groups[first_idx : first_idx + 2] = [groups[group_idx] | groups[neighbor_idx]]

    @classmethod
    def from_json_values(cls, json_values: list[dict[str, Any]]) -> Self:
        """Return the quotas that the output of `to_json_values` holds.

        Raises:
            ValueError: If a group names a value that is not a `DifficultyTier`.
        """
        return cls(counts={frozenset(map(DifficultyTier, group["tiers"])): group["count"] for group in json_values})
