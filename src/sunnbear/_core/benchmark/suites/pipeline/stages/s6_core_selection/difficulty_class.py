"""`DifficultyClass` buckets a candidate by its empirical difficulty index (EDI), relative to bisection's evaluations.

A candidate's EDI is the geometric pseudo-quantile (gpq) at `EDI_GPQ_LEVEL` of the evaluation counts of all its solves
with the core solver configs, each incorrect solve counting as `max_fevals`, a solve's evaluation budget. Relative to
`n_bisection_fevals`, the evaluation count that bisection spends, the classes are:

- A: below 1/4, far better than bisection;
- B: from 1/4 to 1/2;
- C: from 1/2 to 1, comparable to bisection but still better;
- Da: from 1 to 2, worse than bisection;
- Db: from 2 up to 4; 4 is the ratio of `max_fevals` to `n_bisection_fevals`, so every EDI falls in a class.

The Core holds each class in a fixed share of its size, `DifficultyClass.core_share`: a quarter each for A, B and C, and
the last quarter split 3 to 1 between Da and Db, because test problems of class Db are rare and extreme.
"""

from enum import StrEnum
from fractions import Fraction

# A candidate's EDI is the gpq at this level of its evaluation counts, as the module docstring defines it.
EDI_GPQ_LEVEL = 0.5


# ==================================================================================================
#  DifficultyClass
# ==================================================================================================
class DifficultyClass(StrEnum):
    """A `DifficultyClass` names a range of the EDI relative to `n_bisection_fevals`; a candidate's class holds its EDI.

    The ranges follow the order of the members, each starting where the one before it ends.
    """

    A = "A"
    B = "B"
    C = "C"
    DA = "Da"
    DB = "Db"

    @property
    def core_share(self) -> Fraction:
        """Return the fraction of the Core that the class fills when every class fills its own quota."""
        return _CORE_SHARES[self]

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_edi(cls, edi: float, *, n_bisection_fevals: int) -> "DifficultyClass":
        """Return the class whose EDI range holds `edi`; an EDI at or above the range of Da falls in Db."""
        edi_ratio = edi / n_bisection_fevals
        for difficulty_class in cls:
            if edi_ratio < _EDI_RATIO_UPPER_BOUNDS[difficulty_class]:
                return difficulty_class
        return cls.DB


# Each class's EDI range, relative to `n_bisection_fevals`, excludes its upper bound.
_EDI_RATIO_UPPER_BOUNDS = {
    DifficultyClass.A: 1 / 4,
    DifficultyClass.B: 1 / 2,
    DifficultyClass.C: 1,
    DifficultyClass.DA: 2,
    DifficultyClass.DB: 4,
}
_CORE_SHARES = {
    DifficultyClass.A: Fraction(1, 4),
    DifficultyClass.B: Fraction(1, 4),
    DifficultyClass.C: Fraction(1, 4),
    DifficultyClass.DA: Fraction(3, 16),
    DifficultyClass.DB: Fraction(1, 16),
}
