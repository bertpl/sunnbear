"""`DifficultyTierAssignment` gives each candidate of 1 pool the tier whose quota it counts toward in 1 selection.

`DifficultyTierAssignment.from_pool` orders the pool's candidates by EDI and, where the pool cannot meet a quota, moves
the limits between consecutive tiers in that order, so that the selection can meet every quota.
"""

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self

import numpy as np

from sunnbear._core.problems.core import ProblemId

from .candidate_pool import CandidatePool
from .difficulty_tier import DifficultyTier
from .difficulty_tier_quotas import DifficultyTierQuotas


# ==================================================================================================
#  DifficultyTierAssignment
# ==================================================================================================
@dataclass(frozen=True)
class DifficultyTierAssignment:
    """A `DifficultyTierAssignment` gives each candidate of 1 pool its assigned tier in 1 selection.

    A candidate's assigned tier is the tier whose quota it counts toward. The assigned tier is the candidate's
    difficulty tier, unless the pool holds too few candidates of some tier for its quota: then `from_pool` assigns some
    candidates another tier, by the order of their EDIs.

    Attributes:
        quotas: The quotas of the selection.
        assigned_tiers: Each candidate's assigned tier, keyed by id, in the order of the pool.
        edi_range_by_tier: Per tier, in the order of `DifficultyTier`, the smallest and the largest EDI of the
            candidates with that assigned tier.
    """

    quotas: DifficultyTierQuotas
    assigned_tiers: Mapping[ProblemId, DifficultyTier]
    edi_range_by_tier: Mapping[DifficultyTier, tuple[float, float]]

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _nearest_tier_with_surplus(
        tier_below_quota: DifficultyTier,
        assigned_tier_counts: Mapping[DifficultyTier, int],
        quotas: DifficultyTierQuotas,
        sorted_edis: np.ndarray,
        n_bisection_fevals: int,
    ) -> DifficultyTier:
        """Return the tier from which `tier_below_quota` takes its next candidate: the nearest tier with a surplus.

        A tier has a surplus when it holds more candidates than its quota, and "nearest" counts tiers, not EDIs. When 2
        tiers with a surplus lie equally near on both sides, the tier on the side whose adjacent candidate has the EDI
        closer, as a ratio, to the EDI range of `tier_below_quota` wins, and the lower tier on a tie.

        Args:
            tier_below_quota: A tier that holds fewer candidates than its quota.
            assigned_tier_counts: The number of candidates of each assigned tier, in the order of `DifficultyTier`.
            quotas: The quotas of the selection.
            sorted_edis: The pool's EDIs in ascending order, with the pool's order kept among equal EDIs.
            n_bisection_fevals: The `n_bisection_fevals` that sets the tiers' EDI ranges.
        """
        tiers = list(DifficultyTier)
        position = tiers.index(tier_below_quota)
        quota_by_tier = quotas.quota_by_tier
        surplus_positions = [idx for idx, tier in enumerate(tiers) if assigned_tier_counts[tier] > quota_by_tier[tier]]
        # Of 2 tiers equally near, `min` takes the lower one; `opposite_position` is then the position at the same
        # distance on the other side of `tier_below_quota`.
        nearest_position = min(surplus_positions, key=lambda idx: (abs(idx - position), idx))
        opposite_position = 2 * position - nearest_position
        if opposite_position not in surplus_positions:
            return tiers[nearest_position]
        else:
            # The adjacent candidates of `tier_below_quota` are the last one before its candidates and the first one
            # after them.
            start = sum(assigned_tier_counts[tier] for tier in tiers[:position])
            end = start + assigned_tier_counts[tier_below_quota]
            lower_ratio_distance = tier_below_quota.edi_ratio_distance(sorted_edis[start - 1], n_bisection_fevals)
            upper_ratio_distance = tier_below_quota.edi_ratio_distance(sorted_edis[end], n_bisection_fevals)
            if upper_ratio_distance < lower_ratio_distance:
                return tiers[opposite_position]
            else:
                return tiers[nearest_position]

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_pool(cls, candidate_pool: CandidatePool, quotas: DifficultyTierQuotas) -> Self:
        """Return the assignment of the candidates of `candidate_pool` for a selection under `quotas`.

        The candidates are ordered by EDI, and by their order in the pool where 2 EDIs are equal. In that order, each
        tier's candidates follow those of the tier before it, so the count of candidates per tier is enough to give
        every candidate its assigned tier.

        The number of candidates of each assigned tier starts at the pool's count of that difficulty tier. A tier has a
        surplus when it holds more candidates than its quota. While a tier is below its quota, 1 candidate moves:

        - the tier below its quota with the largest shortfall, the first in the order of `DifficultyTier` on a tie,
          takes 1 candidate from the nearest tier with a surplus, counted in tiers;
        - each tier in between passes 1 candidate on and keeps its number of candidates, so each limit between
          consecutive tiers, from the tier with a surplus to the tier below its quota, moves by 1 candidate;
        - when 2 tiers with a surplus lie equally near on both sides, the tier below its quota takes, of the 2
          candidates just outside its own candidates, the one whose EDI lies closer, as a ratio, to the EDI range of
          the tier below its quota, and the one with the lower EDI on a tie.

        Each move lowers the total shortfall by 1 and puts no other tier below its quota, so the loop ends.

        Raises:
            ValueError: If the pool holds fewer candidates than the selection.
        """
        problem_ids = candidate_pool.feature_matrix.problem_ids
        if len(problem_ids) < quotas.selection_size:
            raise ValueError(
                f"A pool of {len(problem_ids)} candidates cannot fill a selection of {quotas.selection_size}."
            )
        else:
            quota_by_tier = quotas.quota_by_tier
            difficulty_tier_counts = Counter(candidate_pool.difficulty_tiers.values())
            assigned_tier_counts = {tier: difficulty_tier_counts[tier] for tier in DifficultyTier}
            # A stable sort keeps the pool's order among equal EDIs.
            edi_order = np.argsort(candidate_pool.edis, kind="stable")
            sorted_edis = candidate_pool.edis[edi_order]

            # --- moves of 1 candidate -----------
            while any(assigned_tier_counts[tier] < quota for tier, quota in quota_by_tier.items()):
                # `max` takes the first of the tiers with the largest shortfall.
                tier_below_quota = max(
                    DifficultyTier, key=lambda tier: quota_by_tier[tier] - assigned_tier_counts[tier]
                )
                tier_with_surplus = cls._nearest_tier_with_surplus(
                    tier_below_quota, assigned_tier_counts, quotas, sorted_edis, candidate_pool.n_bisection_fevals
                )
                assigned_tier_counts[tier_with_surplus] -= 1
                assigned_tier_counts[tier_below_quota] += 1

            # --- assigned tiers -----------------
            counts = list(assigned_tier_counts.values())
            ends = np.cumsum(counts)
            starts = ends - counts
            assigned_tier_by_row = np.empty(len(problem_ids), dtype=object)
            assigned_tier_by_row[edi_order] = np.repeat(np.array(list(DifficultyTier), dtype=object), counts)
            return cls(
                quotas=quotas,
                assigned_tiers=dict(zip(problem_ids, assigned_tier_by_row.tolist(), strict=True)),
                edi_range_by_tier={
                    tier: (float(sorted_edis[start]), float(sorted_edis[end - 1]))
                    for tier, start, end in zip(DifficultyTier, starts, ends, strict=True)
                },
            )
