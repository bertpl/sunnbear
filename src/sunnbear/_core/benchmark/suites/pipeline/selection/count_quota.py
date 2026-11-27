"""`CountQuota` is a quota for 1 selection: how many of the selected candidates its group may hold."""

from collections.abc import Collection, Mapping
from dataclasses import dataclass

from max_div import Constraint

from sunnbear._core.problems.core import ProblemId

from .quota_fulfillment import QuotaFulfillment


# ==================================================================================================
#  CountQuota
# ==================================================================================================
@dataclass(frozen=True)
class CountQuota:
    """A `CountQuota` gives the smallest and the largest number of selected candidates that may count toward it.

    Attributes:
        group_label: The label of the quota's group of candidates.
        member_ids: The ids of the pool's candidates that belong to the quota's group, selected or not.
        min_count: The smallest number of selected candidates that must count toward the quota.
        max_count: The largest number of selected candidates that may count toward the quota.
    """

    group_label: str
    member_ids: frozenset[ProblemId]
    min_count: int
    max_count: int

    def fulfillment(self, selected_problem_ids: Collection[ProblemId]) -> QuotaFulfillment:
        """Return the quota's smallest and largest count, with the number of `selected_problem_ids` in its group."""
        return QuotaFulfillment(
            group_label=self.group_label,
            min_count=self.min_count,
            max_count=self.max_count,
            n_selected_in_group=len(self.member_ids.intersection(selected_problem_ids)),
        )

    def to_constraint(self, row_index_by_problem_id: Mapping[ProblemId, int]) -> Constraint:
        """Return the quota as a max-div constraint on the rows that `row_index_by_problem_id` gives its group.

        max-div refuses a constraint whose smallest count exceeds its number of candidates. No selection meets a quota
        whose group holds fewer candidates than its smallest count; with the smallest count lowered to the group's
        size, max-div still selects every candidate of the group, and the fulfillment, which keeps the quota's own
        smallest count, records that the selection misses the quota.

        Raises:
            ValueError: If the group holds no candidates, because max-div refuses a constraint on no candidates.
        """
        return Constraint(
            int_set={row_index_by_problem_id[problem_id] for problem_id in self.member_ids},
            min_count=min(self.min_count, len(self.member_ids)),
            max_count=self.max_count,
        )
