"""`QuotaFulfillment` records 1 quota of a selection: its counts, and how many selected candidates count toward it."""

from dataclasses import dataclass
from typing import Any, Self


# ==================================================================================================
#  QuotaFulfillment
# ==================================================================================================
@dataclass(frozen=True)
class QuotaFulfillment:
    """A `QuotaFulfillment` records 1 quota's counts, and the number of selected candidates that count toward it.

    Attributes:
        label: The label of the quota's group of candidates.
        min_count: The smallest number of selected candidates that must count toward the quota.
        max_count: The largest number of selected candidates that may count toward the quota.
        n_selected: The number of selected candidates that count toward the quota.
    """

    label: str
    min_count: int
    max_count: int
    n_selected: int

    @property
    def is_met(self) -> bool:
        """Return whether `n_selected` lies from `min_count` up to `max_count`."""
        return self.min_count <= self.n_selected <= self.max_count

    # --------------------------------------------------------------------------
    #  Files
    # --------------------------------------------------------------------------
    def to_json_values(self) -> dict[str, Any]:
        """Return the fulfillment as JSON values, 1 key per attribute."""
        return {
            "label": self.label,
            "min_count": self.min_count,
            "max_count": self.max_count,
            "n_selected": self.n_selected,
        }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_json_values(cls, json_values: dict[str, Any]) -> Self:
        """Return the fulfillment that the output of `to_json_values` holds."""
        return cls(
            label=json_values["label"],
            min_count=json_values["min_count"],
            max_count=json_values["max_count"],
            n_selected=json_values["n_selected"],
        )
