"""`QuotaFulfillment` records 1 quota of a selection, and how many selected candidates count toward it."""

from dataclasses import dataclass


# ==================================================================================================
#  QuotaFulfillment
# ==================================================================================================
@dataclass(frozen=True)
class QuotaFulfillment:
    """A `QuotaFulfillment` records 1 quota of a selection, and how many selected candidates count toward it.

    The selection meets the quota when `n_selected_in_group` lies between `min_count` and `max_count`, both included.

    Attributes:
        group_label: The label of the quota's group of candidates.
        min_count: The smallest number of selected candidates that must count toward the quota.
        max_count: The largest number of selected candidates that may count toward the quota.
        n_selected_in_group: The number of selected candidates that count toward the quota.
    """

    group_label: str
    min_count: int
    max_count: int
    n_selected_in_group: int
