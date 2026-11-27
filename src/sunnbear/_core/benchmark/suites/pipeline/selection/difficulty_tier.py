"""`DifficultyTier` buckets a candidate by its empirical difficulty index (EDI), relative to bisection's evaluations.

A candidate's EDI is computed by `compute_edi`, from the evaluation counts of all its solves with the core solver
configs. Relative to `n_bisection_fevals`, the evaluation count that bisection spends, the tiers are:

- A: below 1/4, far better than bisection;
- B: from 1/4 to 1/2;
- C: from 1/2 to 1, comparable to bisection but still better;
- D: from 1 up to 4, worse than bisection; 4 is the ratio of `max_fevals` to `n_bisection_fevals`, so every EDI falls
  in a tier.

D spans a factor 4, where B and C each span a factor 2, because an EDI above twice `n_bisection_fevals` is rare, so a
separate tier from 2 to 4 would hold few candidates: of the core solver configs, ITP spends at most about
`n_bisection_fevals` evaluations, and Ridders at most about twice that.
"""

from enum import StrEnum


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
    D = "D"

    def edi_range(self, n_bisection_fevals: int) -> tuple[float, float]:
        """Return the tier's range of the EDI, `(lower, upper)`, for solves with `n_bisection_fevals`.

        The range holds its lower bound and excludes its upper bound; A's range starts at 0.
        """
        lower_ratio, upper_ratio = _EDI_RATIO_RANGES[self]
        return lower_ratio * n_bisection_fevals, upper_ratio * n_bisection_fevals

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_edi(cls, edi: float, *, n_bisection_fevals: int) -> "DifficultyTier":
        """Return the tier whose EDI range holds `edi`; an EDI at or above the upper end of D's range falls in D."""
        for difficulty_tier in cls:
            if edi < difficulty_tier.edi_range(n_bisection_fevals)[1]:
                return difficulty_tier
        return cls.D


# Each tier's EDI range, relative to `n_bisection_fevals`, starts where the range of the tier before it ends.
_EDI_RATIO_RANGES = {
    DifficultyTier.A: (0, 1 / 4),
    DifficultyTier.B: (1 / 4, 1 / 2),
    DifficultyTier.C: (1 / 2, 1),
    DifficultyTier.D: (1, 4),
}
