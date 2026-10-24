"""This module lists the formulas of category 1 that have a modified version, and how each version is modified.

A formula of category 1 has a modified version when some of its published test functions fail the validation of the
benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`. The class docstring of `PublishedTestFunctions`
describes the parameter `modified` that such a formula has. Such a formula's module is written by hand, starting from
its generated module.
"""

from enum import StrEnum


# ==================================================================================================
#  ModificationType
# ==================================================================================================
class ModificationType(StrEnum):
    """A `ModificationType` names how a formula's test functions with ``modified = 1`` differ from published ones."""

    # The modified function adds the parameter c of category 1 to the published function's value, on the published
    # interval, and does not shift x.
    C_ADDS_TO_F = "c_adds_to_f"


# MODIFIED_FORMULAS holds the type of modification of each formula of category 1 that has the parameter `modified`.
MODIFIED_FORMULAS = {
    "f1.1.2.4": ModificationType.C_ADDS_TO_F,
    "f1.2.15.1": ModificationType.C_ADDS_TO_F,
    "f1.2.15.2": ModificationType.C_ADDS_TO_F,
    "f1.3.2.3": ModificationType.C_ADDS_TO_F,
    "f1.3.3.30": ModificationType.C_ADDS_TO_F,
    "f1.3.3.33": ModificationType.C_ADDS_TO_F,
    "f1.4.6.20": ModificationType.C_ADDS_TO_F,
    "f1.4.7.9": ModificationType.C_ADDS_TO_F,
}
