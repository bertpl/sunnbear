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
    def _choose_supplier(
        short_idx: int,
        assigned_tier_counts: list[int],
        quota_counts: list[int],
        sorted_edis: np.ndarray,
        n_bisection_fevals: int,
    ) -> int:
        """Return the index, in the order of `DifficultyTier`, of the tier that gives 1 candidate to the short tier.

        The rule is the one that `from_pool` describes.

        Args:
            short_idx: The index of the short tier, which holds fewer candidates than its quota.
            assigned_tier_counts: The number of candidates of each assigned tier, in the order of `DifficultyTier`.
            quota_counts: The quota of each tier, in the same order.
            sorted_edis: The pool's EDIs in ascending order, with the pool's order kept among equal EDIs.
            n_bisection_fevals: The `n_bisection_fevals` that sets the tiers' EDI ranges.
        """
        surplus_idxs = [
            idx
            for idx, (count, quota) in enumerate(zip(assigned_tier_counts, quota_counts, strict=True))
            if count > quota
        ]
        # Of 2 tiers equally near, `min` takes the lower one; `opposite_idx` is then the tier at the same distance on
        # the other side of the short tier.
        nearest_idx = min(surplus_idxs, key=lambda idx: (abs(idx - short_idx), idx))
        opposite_idx = 2 * short_idx - nearest_idx
        if opposite_idx not in surplus_idxs:
            return nearest_idx
        else:
            # The 2 candidates just outside the short tier's candidates are the last one before them and the first one
            # after them.
            start = sum(assigned_tier_counts[:short_idx])
            end = start + assigned_tier_counts[short_idx]
            short_tier = list(DifficultyTier)[short_idx]
            lower_ratio_distance = short_tier.edi_ratio_distance(sorted_edis[start - 1], n_bisection_fevals)
            upper_ratio_distance = short_tier.edi_ratio_distance(sorted_edis[end], n_bisection_fevals)
            if upper_ratio_distance < lower_ratio_distance:
                return opposite_idx
            else:
                return nearest_idx

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
        surplus when it holds more candidates than its quota. While a tier holds fewer candidates than its quota, 1
        candidate moves:

        - the tier with the largest shortfall, the first in the order of `DifficultyTier` on a tie, takes 1 candidate
          from the nearest tier with a surplus, counted in tiers;
        - each tier in between passes 1 candidate on and keeps its number of candidates, so each limit between
          consecutive tiers, from the supplying tier to the short tier, moves by 1 candidate;
        - when 2 tiers with a surplus lie equally near on both sides, the short tier takes, of the 2 candidates just
          outside its own candidates, the one whose EDI lies closer, as a ratio, to the short tier's EDI range, and
          the one with the lower EDI on a tie.

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
            difficulty_tier_counts = Counter(candidate_pool.difficulty_tiers.values())
            assigned_tier_counts = [difficulty_tier_counts[tier] for tier in tiers]
            # A stable sort keeps the pool's order among equal EDIs.
            edi_order = np.argsort(candidate_pool.edis, kind="stable")
            sorted_edis = candidate_pool.edis[edi_order]

            # --- moves of 1 candidate -----------
            while any(count < quota for count, quota in zip(assigned_tier_counts, quota_counts, strict=True)):
                shortfalls = [quota - count for count, quota in zip(assigned_tier_counts, quota_counts, strict=True)]
                short_idx = shortfalls.index(max(shortfalls))
                supplier_idx = cls._choose_supplier(
                    short_idx, assigned_tier_counts, quota_counts, sorted_edis, candidate_pool.n_bisection_fevals
                )
                assigned_tier_counts[supplier_idx] -= 1
                assigned_tier_counts[short_idx] += 1

            # --- assigned tiers -----------------
            ends = np.cumsum(assigned_tier_counts)
            starts = ends - assigned_tier_counts
            assigned_tier_by_row = np.empty(len(problem_ids), dtype=object)
            assigned_tier_by_row[edi_order] = np.repeat(np.array(tiers, dtype=object), assigned_tier_counts)
            return cls(
                quotas=quotas,
                assigned_tiers=dict(zip(problem_ids, assigned_tier_by_row.tolist(), strict=True)),
                edi_range_by_tier={
                    tier: (float(sorted_edis[start]), float(sorted_edis[end - 1]))
                    for tier, start, end in zip(tiers, starts, ends, strict=True)
                },
            )
