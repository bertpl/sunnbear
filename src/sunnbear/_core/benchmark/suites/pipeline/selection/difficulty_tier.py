"""`DifficultyTier` buckets a candidate by its empirical difficulty index (EDI), relative to bisection's evaluations.

A candidate's EDI is computed by `compute_edi`, from the evaluation counts of all its solves with the core solver
configs. Relative to `n_bisection_fevals`, the evaluation count that bisection spends, the tiers are:

- A: below 1/4, far better than bisection;
- B: from 1/4 to 1/2;
- C: from 1/2 to 1, comparable to bisection but still better;
- Da: from 1 to 2, worse than bisection;
- Db: from 2 up to 4; 4 is the ratio of `max_fevals` to `n_bisection_fevals`, so every EDI falls in a tier.

The Core that ships holds each tier in a fixed share of its size, `DifficultyTier.core_share`: a quarter each for A, B
and C, and the last quarter split 3 to 1 between Da and Db, because test problems of tier Db are rare and extreme.
"""

from enum import StrEnum
from fractions import Fraction


# ==================================================================================================
#  DifficultyTier
# ==================================================================================================
class DifficultyTier(StrEnum):
    """A `DifficultyTier` names a range of the EDI relative to `n_bisection_fevals`.

    A candidate's tier is the range that holds its EDI. The ranges follow the order of the members, each starting where
    the one before it ends.
    """

    A = "A"
    B = "B"
    C = "C"
    DA = "Da"
    DB = "Db"

    @property
    def core_share(self) -> Fraction:
        """Return the fraction of a suite that the tier fills when every tier has a quota of its own."""
        return _CORE_SHARES[self]

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_edi(cls, edi: float, *, n_bisection_fevals: int) -> "DifficultyTier":
        """Return the tier whose EDI range holds `edi`; an EDI at or above the range of Da falls in Db."""
        edi_ratio = edi / n_bisection_fevals
        for difficulty_tier in cls:
            if edi_ratio < _EDI_RATIO_UPPER_BOUNDS[difficulty_tier]:
                return difficulty_tier
        return cls.DB


# Each tier's EDI range, relative to `n_bisection_fevals`, excludes its upper bound.
_EDI_RATIO_UPPER_BOUNDS = {
    DifficultyTier.A: 1 / 4,
    DifficultyTier.B: 1 / 2,
    DifficultyTier.C: 1,
    DifficultyTier.DA: 2,
    DifficultyTier.DB: 4,
}
_CORE_SHARES = {
    DifficultyTier.A: Fraction(1, 4),
    DifficultyTier.B: Fraction(1, 4),
    DifficultyTier.C: Fraction(1, 4),
    DifficultyTier.DA: Fraction(3, 16),
    DifficultyTier.DB: Fraction(1, 16),
}
