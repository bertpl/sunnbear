"""`CoreComposition` holds the size and difficulty quotas of the largest Core that the candidates can fill.

The Core that ships has size `MAX_CORE_SIZE`, with a quota for each `DifficultyClass` at its `core_share`. While the
corpus of formulas grows, the candidates may not fill a Core of that size, so `CoreComposition.from_class_counts` makes
a best effort:

- **size:** the largest of `CORE_SIZES` at which A, B and C each fill a quarter of the Core, and Da and Db together the
  last quarter;
- **quotas:** 1 quota per class at its `core_share`, when Da and Db each have enough candidates for their own quota;
  otherwise 1 shared quota for Da and Db together, at a quarter of the Core, with a `CoreCompositionWarning` that names
  the class that lacks candidates. A quota for only the class that has enough candidates would leave the rest of the
  last quarter without a quota;
- **below the smallest size** the pipeline stops with a message that names each class that lacks candidates, so that a
  maintainer knows which classes need more candidates in the corpus.

Any Core other than one of `MAX_CORE_SIZE` with a quota per class is interim, and never ships.
"""

import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyClass, DifficultyQuota, SuiteComposition

# Every Core size is a power of 2, so that every quota, the size times a `DifficultyClass.core_share`, is a whole number
# of candidates.
CORE_SIZES = (128, 256, 512, 1024, 2048)
MAX_CORE_SIZE = max(CORE_SIZES)
# The Core's size is chosen per quarter of the Core, and each quarter is filled by the classes of 1 entry of
# `_CLASSES_PER_QUARTER`.
_QUARTER = Fraction(1, 4)
_CLASSES_PER_QUARTER = (
    frozenset({DifficultyClass.A}),
    frozenset({DifficultyClass.B}),
    frozenset({DifficultyClass.C}),
    frozenset({DifficultyClass.DA, DifficultyClass.DB}),
)


# ==================================================================================================
#  CoreComposition
# ==================================================================================================
@dataclass(frozen=True)
class CoreComposition(SuiteComposition):
    """A `CoreComposition` is the Core's `SuiteComposition`, plus the number of input candidates of each class.

    The Core's size is 1 of `CORE_SIZES`.

    Attributes:
        class_counts: The number of candidates of each `DifficultyClass` among which the Core is selected.
    """

    class_counts: Mapping[DifficultyClass, int]

    @property
    def is_interim(self) -> bool:
        """Return whether the Core is not one that ships: not of `MAX_CORE_SIZE`, or without a quota per class."""
        return (self.size != MAX_CORE_SIZE) or (len(self.quotas) != len(DifficultyClass))

    def report_row(self) -> dict[str, int | bool | None]:
        """Return the Core's size and whether it is interim, and per class its quota, count and largest Core size.

        The keys are the column names of the report that core selection writes:

        - ``core_size`` and ``is_interim``;
        - per class, with the class's value in lower case:
          - ``quota_<class>``, null where the class shares its quota;
          - ``n_candidates_<class>``;
          - ``max_core_size_<class>``, the largest of `CORE_SIZES` at which the class's candidates fill its
            `core_share` on their own, null where they fill it at none;
        - for Da and Db together: ``quota_d``, null where each has its own quota, and ``max_core_size_d``, the largest
          of `CORE_SIZES` at which their candidates together fill a quarter of the Core, null where they fill none.
        """
        count_by_quota_classes = {quota.classes: quota.count for quota in self.quotas}
        row: dict[str, int | bool | None] = {"core_size": self.size, "is_interim": self.is_interim}
        for difficulty_class in DifficultyClass:
            name = difficulty_class.value.lower()
            n_candidates = self.class_counts[difficulty_class]
            row[f"quota_{name}"] = count_by_quota_classes.get(frozenset({difficulty_class}))
            row[f"n_candidates_{name}"] = n_candidates
            row[f"max_core_size_{name}"] = self._max_core_size(n_candidates, difficulty_class.core_share)
        d_classes = _CLASSES_PER_QUARTER[-1]
        row["quota_d"] = count_by_quota_classes.get(d_classes)
        row["max_core_size_d"] = self._max_core_size(sum(self.class_counts[c] for c in d_classes), _QUARTER)
        return row

    def report_table(self) -> pl.DataFrame:
        """Return the report that core selection writes: 1 row with the columns of `report_row`."""
        row = self.report_row()
        return pl.DataFrame([row], schema={name: pl.Boolean() if name == "is_interim" else pl.Int64() for name in row})

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _max_core_size(n_candidates: int, core_share: Fraction) -> int | None:
        """Return the largest of `CORE_SIZES` at which `n_candidates` fill the fraction `core_share`, else ``None``."""
        return max((size for size in CORE_SIZES if n_candidates >= size * core_share), default=None)

    @staticmethod
    def _describe_short_quarters(n_candidates_per_quarter: list[int], core_size: int) -> str:
        """Return the reason to stop: each quarter of a Core of `core_size` that lacks candidates, and how many."""
        quarter_size = int(core_size * _QUARTER)
        shortfalls = "; ".join(
            f"{'class' if len(classes) == 1 else 'classes'} {' and '.join(sorted(c.value for c in classes))} "
            f"{'has' if len(classes) == 1 else 'have'} {n_candidates} candidates, "
            f"{quarter_size - n_candidates} short of {quarter_size}"
            for classes, n_candidates in zip(_CLASSES_PER_QUARTER, n_candidates_per_quarter, strict=True)
            if n_candidates < quarter_size
        )
        return f"The candidates fill no Core of {core_size} or more: {shortfalls}."

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_class_counts(cls, class_counts: Mapping[DifficultyClass, int]) -> "CoreComposition":
        """Return the largest Core, with its quotas, that the candidates counted in `class_counts` can fill.

        Args:
            class_counts: The number of candidates of each `DifficultyClass`; a missing class has none.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest of `CORE_SIZES`; the message names each
                quarter of that Core that is short, and by how many candidates.

        Warns:
            CoreCompositionWarning: If Da or Db cannot fill its own quota, so that the 2 classes share 1 quota.
        """
        counts = {difficulty_class: class_counts.get(difficulty_class, 0) for difficulty_class in DifficultyClass}

        # --- size: every quarter filled ---------
        n_candidates_per_quarter = [sum(counts[c] for c in classes) for classes in _CLASSES_PER_QUARTER]
        core_size = cls._max_core_size(min(n_candidates_per_quarter), _QUARTER)
        if core_size is None:
            raise PipelineStopError(cls._describe_short_quarters(n_candidates_per_quarter, min(CORE_SIZES)))

        # --- quotas -----------------------------
        short_d_classes = [c for c in _CLASSES_PER_QUARTER[-1] if counts[c] < core_size * c.core_share]
        if short_d_classes:
            shortfalls = "; ".join(
                f"class {c.value} has {counts[c]} candidates, {int(core_size * c.core_share) - counts[c]} short of "
                f"its quota of {int(core_size * c.core_share)}"
                for c in sorted(short_d_classes)
            )
            warnings.warn(
                f"At Core size {core_size}, {shortfalls}; classes Da and Db share 1 quota of "
                f"{int(core_size * _QUARTER)} candidates.",
                CoreCompositionWarning,
                stacklevel=2,
            )
            quotas = tuple(
                DifficultyQuota(classes=classes, count=int(core_size * _QUARTER)) for classes in _CLASSES_PER_QUARTER
            )
        else:
            quotas = tuple(
                DifficultyQuota(classes=frozenset({c}), count=int(core_size * c.core_share)) for c in DifficultyClass
            )
        return cls(quotas=quotas, class_counts=counts)


# ==================================================================================================
#  CoreCompositionWarning
# ==================================================================================================
class CoreCompositionWarning(UserWarning):
    """`CoreComposition.from_class_counts` warns with `CoreCompositionWarning` when Da and Db share 1 quota."""
