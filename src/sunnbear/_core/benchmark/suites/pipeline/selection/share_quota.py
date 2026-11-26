"""`ShareQuota` is a quota as a stage declares it: the shares of a selection that a group of candidates may hold."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Self

from .candidate_group import CandidateGroup
from .candidate_pool import CandidatePool
from .count_quota import CountQuota


# ==================================================================================================
#  ShareQuota
# ==================================================================================================
@dataclass(frozen=True)
class ShareQuota:
    """A `ShareQuota` gives a group of candidates the smallest and the largest share of a selection that it may hold.

    The shares hold for every size of selection, so a stage declares a series' quotas once for all its suites, and
    `for_selection` turns each into the counts of 1 selection.

    Attributes:
        group: The group of candidates that count toward the quota.
        min_share: The smallest share of the selection that the group's candidates must hold.
        max_share: The largest share of the selection that the group's candidates may hold.
    """

    group: CandidateGroup
    min_share: Fraction
    max_share: Fraction

    def __post_init__(self) -> None:
        """Refuse shares outside the range from 0 to 1, and a smallest share above the largest.

        Raises:
            ValueError: If the shares do not satisfy ``0 <= min_share <= max_share <= 1``.
        """
        if not 0 <= self.min_share <= self.max_share <= 1:
            raise ValueError(
                f"The shares of the quota of group {self.group.label} must satisfy 0 <= min_share <= max_share <= 1; "
                f"they are {self.min_share} and {self.max_share}."
            )

    def for_selection(self, candidate_pool: CandidatePool, *, selection_size: int) -> CountQuota:
        """Return the quota's counts for a selection of `selection_size` candidates from `candidate_pool`.

        Raises:
            ValueError: If a share of `selection_size` is not a whole number of candidates.
        """
        min_count = self.min_share * selection_size
        max_count = self.max_share * selection_size
        if min_count.denominator != 1 or max_count.denominator != 1:
            raise ValueError(
                f"The shares {self.min_share} and {self.max_share} of the quota of group {self.group.label} give no "
                f"whole number of candidates in a selection of {selection_size}."
            )
        else:
            return CountQuota(
                label=self.group.label,
                problem_ids=frozenset(self.group.member_ids(candidate_pool)),
                min_count=int(min_count),
                max_count=int(max_count),
            )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def exactly(cls, group: CandidateGroup, share: Fraction) -> Self:
        """Return the quota under which the candidates of `group` hold exactly `share` of the selection."""
        return cls(group=group, min_share=share, max_share=share)

    @classmethod
    def at_least(cls, group: CandidateGroup, share: Fraction) -> Self:
        """Return the quota under which the candidates of `group` hold at least `share` of the selection."""
        return cls(group=group, min_share=share, max_share=Fraction(1))
