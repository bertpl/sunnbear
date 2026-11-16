"""`DifficultyTierAssignment` gives each candidate of 1 pool the tier whose quota it counts toward in 1 selection.

`DifficultyTierAssignment.from_pool` moves the limits between the tiers' candidates where the pool cannot meet a quota,
so that the selection can meet every quota.
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

    A candidate's assigned tier is the tier whose quota it counts toward. It is the candidate's difficulty tier, unless
    the pool holds too few candidates of some tier for its quota: then `from_pool` assigns some candidates a
    neighboring tier, by the order of their EDIs.

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
    def _choose_supplier(
        short_idx: int,
        tier_counts: list[int],
        quota_counts: list[int],
        sorted_edis: np.ndarray,
        n_bisection_fevals: int,
    ) -> int:
        """Return the index, in the order of `DifficultyTier`, of the tier that gives 1 candidate to a short tier.

        The supplier is the nearest tier, counted in tiers, whose count exceeds its quota. When the nearest such tiers
        lie equally near on both sides, the short tier takes the adjacent candidate whose EDI lies closer, as a ratio,
        to the short tier's EDI range; the lower side on a tie.

        Args:
            short_idx: The index of the short tier.
            tier_counts: The number of candidates of each tier, in the order of `DifficultyTier`.
            quota_counts: The quota of each tier, in the same order.
            sorted_edis: The pool's EDIs, in the order of `from_pool`.
            n_bisection_fevals: The `n_bisection_fevals` that sets the tiers' EDI ranges.
        """
        surplus_idxs = [
            idx for idx, (count, quota) in enumerate(zip(tier_counts, quota_counts, strict=True)) if count > quota
        ]
        # Of 2 tiers equally near, `min` takes the lower one; the tier as near on the other side then mirrors it.
        nearest_idx = min(surplus_idxs, key=lambda idx: (abs(idx - short_idx), idx))
        mirror_idx = 2 * short_idx - nearest_idx
        if mirror_idx not in surplus_idxs:
            return nearest_idx
        else:
            # The adjacent candidates on both sides are the last one before the short tier's candidates and the first
            # one after them. A ratio distance of 1 means that the EDI lies in the range.
            start = sum(tier_counts[:short_idx])
            end = start + tier_counts[short_idx]
            lower_edi, upper_edi = sorted_edis[start - 1], sorted_edis[end]
            range_lower, range_upper = list(DifficultyTier)[short_idx].edi_range(n_bisection_fevals)
            lower_ratio_distance = max(range_lower / lower_edi, lower_edi / range_upper, 1.0)
            upper_ratio_distance = max(range_lower / upper_edi, upper_edi / range_upper, 1.0)
            if upper_ratio_distance < lower_ratio_distance:
                return mirror_idx
            else:
                return nearest_idx

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_pool(cls, candidate_pool: CandidatePool, quotas: DifficultyTierQuotas) -> Self:
        """Return the assignment of the candidates of `candidate_pool` for a selection under `quotas`.

        The candidates are ordered by EDI, and by their order in the pool where 2 EDIs are equal. In that order, each
        tier's candidates follow those of the tier before it, so the number of candidates of each tier sets every
        candidate's assigned tier. The numbers start at the pool's count of each difficulty tier. While a tier holds
        fewer candidates than its quota, 1 candidate moves:

        - the tier with the largest shortfall, the first in the order of `DifficultyTier` on a tie, takes 1 candidate
          from the nearest tier, counted in tiers, whose candidates exceed its quota;
        - each tier in between passes 1 candidate on and keeps its number, so each limit between the 2 tiers'
          candidates moves by 1 candidate;
        - when such tiers lie equally near on both sides, the short tier takes the adjacent candidate whose EDI lies
          closer, as a ratio, to the tier's EDI range.

        Each move lowers the total shortfall by 1 and leaves no other tier short, so the loop ends.

        Raises:
            ValueError: If the pool holds fewer candidates than the selection.
        """
        problem_ids = candidate_pool.feature_matrix.problem_ids
        if len(problem_ids) < quotas.selection_size:
            raise ValueError(
                f"A pool of {len(problem_ids)} candidates cannot fill a selection of {quotas.selection_size}."
            )
        else:
            tiers = list(DifficultyTier)
            quota_counts = list(quotas.quota_by_tier.values())
            pool_tier_counts = Counter(candidate_pool.difficulty_tiers)
            tier_counts = [pool_tier_counts[tier] for tier in tiers]
            # A stable sort keeps the pool's order among equal EDIs.
            edi_order = np.argsort(candidate_pool.edis, kind="stable")
            sorted_edis = candidate_pool.edis[edi_order]

            # --- moves of 1 candidate ---------------
            while any(count < quota for count, quota in zip(tier_counts, quota_counts, strict=True)):
                shortfalls = [quota - count for count, quota in zip(tier_counts, quota_counts, strict=True)]
                short_idx = shortfalls.index(max(shortfalls))
                supplier_idx = cls._choose_supplier(
                    short_idx, tier_counts, quota_counts, sorted_edis, candidate_pool.n_bisection_fevals
                )
                tier_counts[supplier_idx] -= 1
                tier_counts[short_idx] += 1

            # --- assigned tiers ---------------------
            ends = np.cumsum(tier_counts)
            starts = ends - tier_counts
            tier_by_row = np.empty(len(problem_ids), dtype=object)
            tier_by_row[edi_order] = [
                tier for tier, count in zip(tiers, tier_counts, strict=True) for _ in range(count)
            ]
            return cls(
                quotas=quotas,
                assigned_tiers=dict(zip(problem_ids, tier_by_row.tolist(), strict=True)),
                edi_range_by_tier={
                    tier: (float(sorted_edis[start]), float(sorted_edis[end - 1]))
                    for tier, start, end in zip(tiers, starts, ends, strict=True)
                },
            )
