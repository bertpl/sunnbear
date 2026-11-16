"""`DifficultyTier` buckets a candidate by its empirical difficulty index (EDI), relative to bisection's evaluations.

A candidate's EDI is computed by `compute_edi`, from the evaluation counts of all its solves with the core solver
configs. Relative to `n_bisection_fevals`, the evaluation count that bisection spends, the tiers are:

- A: below 1/4, far better than bisection;
- B: from 1/4 to 1/2;
- C: from 1/2 to 1, comparable to bisection but still better;
- Da: from 1 to 2, worse than bisection;
- Db: from 2 up to 4; 4 is the ratio of `max_fevals` to `n_bisection_fevals`, so every EDI falls in a tier.

Every max-div selection, of the Core and of the distilled suites, has 1 quota per tier, a fixed share of the
selection's size, `DifficultyTier.core_share`: a quarter each for A, B and C, and the last quarter split 3 to 1 between
Da and Db, because test problems of tier Db are rare and extreme.
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
        """Return the fraction of the candidates of every selection that count toward the tier's quota."""
        return _CORE_SHARES[self]

    def edi_range(self, n_bisection_fevals: int) -> tuple[float, float]:
        """Return the tier's range of the EDI, `(lower, upper)`, for solves with `n_bisection_fevals`.

        The range holds its lower bound and excludes its upper bound; A's range starts at 0.
        """
        lower_ratio, upper_ratio = _EDI_RATIO_RANGES[self]
        return lower_ratio * n_bisection_fevals, upper_ratio * n_bisection_fevals

    def edi_ratio_distance(self, edi: float, n_bisection_fevals: int) -> float:
        """Return the factor by which `edi` lies below or above the tier's EDI range, or 1 when the range holds it."""
        lower, upper = self.edi_range(n_bisection_fevals)
        return max(lower / edi, edi / upper, 1.0)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_edi(cls, edi: float, *, n_bisection_fevals: int) -> "DifficultyTier":
        """Return the tier whose EDI range holds `edi`; an EDI at or above the range of Da falls in Db."""
        for difficulty_tier in cls:
            if edi < difficulty_tier.edi_range(n_bisection_fevals)[1]:
                return difficulty_tier
        return cls.DB


# Each tier's EDI range, relative to `n_bisection_fevals`, starts where the range of the tier before it ends.
_EDI_RATIO_RANGES = {
    DifficultyTier.A: (0, 1 / 4),
    DifficultyTier.B: (1 / 4, 1 / 2),
    DifficultyTier.C: (1 / 2, 1),
    DifficultyTier.DA: (1, 2),
    DifficultyTier.DB: (2, 4),
}
_CORE_SHARES = {
    DifficultyTier.A: Fraction(1, 4),
    DifficultyTier.B: Fraction(1, 4),
    DifficultyTier.C: Fraction(1, 4),
    DifficultyTier.DA: Fraction(3, 16),
    DifficultyTier.DB: Fraction(1, 16),
}
