"""`CandidateGroup` is a group of candidates; a quota counts how many of its members a selection holds.

`DifficultyTierCandidateGroup` groups the candidates by difficulty tier.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from sunnbear._core.problems.core import ProblemId

from .candidate_pool import CandidatePool
from .difficulty_tier import DifficultyTier


# ==================================================================================================
#  CandidateGroup
# ==================================================================================================
class CandidateGroup(ABC):
    """A `CandidateGroup` is a labeled group of candidates; a quota counts how many of its members a selection holds.

    A group decides from each candidate alone whether the candidate belongs to it, so a candidate's membership does
    not depend on the other candidates of a selection.
    """

    @property
    @abstractmethod
    def label(self) -> str:
        """Return the group's label for a reader, such as ``A+B``."""

    @abstractmethod
    def member_ids(self, candidate_pool: CandidatePool) -> list[ProblemId]:
        """Return the ids of the candidates of `candidate_pool` that belong to the group, in the order of the pool."""


# ==================================================================================================
#  DifficultyTierCandidateGroup
# ==================================================================================================
@dataclass(frozen=True)
class DifficultyTierCandidateGroup(CandidateGroup):
    """A `DifficultyTierCandidateGroup` holds the candidates of 1 or more difficulty tiers.

    A candidate belongs to the group when its difficulty tier, which follows from its EDI alone, is 1 of `tiers`.

    Attributes:
        tiers: The difficulty tiers of the group's candidates, each listed once.
    """

    tiers: tuple[DifficultyTier, ...]

    def __post_init__(self) -> None:
        """Refuse a group without tiers, and a tier listed twice.

        Raises:
            ValueError: If `tiers` is empty or lists a tier twice.
        """
        if not self.tiers or len(set(self.tiers)) != len(self.tiers):
            raise ValueError(f"A group needs 1 or more tiers, each listed once; it has {self.tiers}.")

    @property
    def label(self) -> str:
        """Return the values of the group's tiers in the order of `DifficultyTier`, joined by ``+``, such as ``A+B``."""
        return "+".join(tier.value for tier in DifficultyTier if tier in self.tiers)

    def member_ids(self, candidate_pool: CandidatePool) -> list[ProblemId]:
        """Return the ids of the candidates of `candidate_pool` whose difficulty tier is 1 of `tiers`."""
        return [problem_id for problem_id, tier in candidate_pool.difficulty_tiers.items() if tier in self.tiers]
