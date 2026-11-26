"""`CountQuota` is a quota as 1 selection sees it: how many of the selected candidates its group may hold."""

from collections.abc import Collection
from dataclasses import dataclass

from sunnbear._core.problems.core import ProblemId

from .quota_fulfillment import QuotaFulfillment


# ==================================================================================================
#  CountQuota
# ==================================================================================================
@dataclass(frozen=True)
class CountQuota:
    """A `CountQuota` gives the smallest and the largest number of selected candidates that may count toward it.

    Attributes:
        label: The label of the group of candidates that count toward the quota.
        problem_ids: The candidates that count toward the quota.
        min_count: The smallest number of selected candidates that must count toward the quota.
        max_count: The largest number of selected candidates that may count toward the quota.
    """

    label: str
    problem_ids: frozenset[ProblemId]
    min_count: int
    max_count: int

    def fulfillment(self, selected_problem_ids: Collection[ProblemId]) -> QuotaFulfillment:
        """Return the quota's counts, with the number of `selected_problem_ids` that count toward the quota."""
        return QuotaFulfillment(
            label=self.label,
            min_count=self.min_count,
            max_count=self.max_count,
            n_selected=len(self.problem_ids.intersection(selected_problem_ids)),
        )
