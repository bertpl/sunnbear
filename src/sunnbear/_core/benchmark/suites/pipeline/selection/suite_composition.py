"""`SuiteComposition` holds a suite's difficulty quotas, each a `DifficultyQuota`, whose counts sum to its size.

Every suite of the pipeline has the Core's composition, as `CoreComposition.from_class_counts` chooses it, scaled to
the suite's size.
"""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError

from .difficulty_class import DifficultyClass


# ==================================================================================================
#  SuiteComposition
# ==================================================================================================
@dataclass(frozen=True)
class SuiteComposition:
    """A `SuiteComposition` holds a suite's difficulty quotas.

    Attributes:
        quotas: The suite's difficulty quotas, which together count every `DifficultyClass` once.
    """

    quotas: tuple["DifficultyQuota", ...]

    @property
    def size(self) -> int:
        """Return the number of candidates in the suite: the sum of its quotas' counts."""
        return sum(quota.count for quota in self.quotas)

    def check_selection(self, selected_classes: Sequence[DifficultyClass]) -> None:
        """Stop the pipeline unless a selection of candidates, given by their classes, has the suite's size and quotas.

        Raises:
            PipelineStopError: If `selected_classes` does not hold `size` candidates, or does not meet a quota exactly;
                the message names each such quota with the selection's count.
        """
        class_counts = Counter(selected_classes)
        unmet_quota_descriptions = [
            f"{' and '.join(sorted(c.value for c in quota.classes))}: {sum(class_counts[c] for c in quota.classes)} "
            f"of {quota.count}"
            for quota in self.quotas
            if sum(class_counts[c] for c in quota.classes) != quota.count
        ]
        if len(selected_classes) != self.size or unmet_quota_descriptions:
            raise PipelineStopError(
                f"The selection holds {len(selected_classes)} candidates for a suite of {self.size}; unmet quotas: "
                f"{'; '.join(unmet_quota_descriptions) or 'none'}."
            )

    def halved(self) -> "SuiteComposition":
        """Return the composition of a suite of half the size, with half of each quota.

        Raises:
            ValueError: If a quota's count is odd, so that no suite of half the size holds half of it.
        """
        if any(quota.count % 2 for quota in self.quotas):
            raise ValueError(f"A suite of {self.size} with an odd quota has no composition at half its size.")
        else:
            return SuiteComposition(
                quotas=tuple(DifficultyQuota(classes=quota.classes, count=quota.count // 2) for quota in self.quotas)
            )


# ==================================================================================================
#  DifficultyQuota
# ==================================================================================================
@dataclass(frozen=True)
class DifficultyQuota:
    """A `DifficultyQuota` sets how many of a suite's candidates come from a set of difficulty classes.

    Attributes:
        classes: The quota's classes, counted together: 1 class, or Da and Db when they share 1 quota.
        count: The exact number of the suite's candidates whose class is in `classes`.
    """

    classes: frozenset[DifficultyClass]
    count: int
