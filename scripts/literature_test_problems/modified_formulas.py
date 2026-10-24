"""This module lists the formulas of category 1 that have a modified version, and how each version is modified.

A formula of category 1 has a modified version when some of its published test functions fail the validation of the
benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`. The class docstring of `PublishedTestFunctions`
describes such a formula's parameter `modified`.

Such a formula's module is written by hand, starting from the module that the generator writes for the formula when the
formula is absent from `MODIFIED_FORMULAS`.
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
    # The modified function has its own interval, which changes the published one as little as needed, and c shifts x
    # by the rule of category 1, with the c_scale of that interval.
    CHANGED_INTERVAL = "changed_interval"


# MODIFIED_FORMULAS holds the type of modification of each formula of category 1 that has the parameter `modified`.
MODIFIED_FORMULAS = {
    "f1.1.2.4": ModificationType.C_ADDS_TO_F,
    "f1.1.5.3": ModificationType.CHANGED_INTERVAL,
    "f1.1.12.2": ModificationType.CHANGED_INTERVAL,
    "f1.1.13.21": ModificationType.CHANGED_INTERVAL,
    "f1.2.4.2": ModificationType.CHANGED_INTERVAL,
    "f1.2.15.1": ModificationType.C_ADDS_TO_F,
    "f1.2.15.2": ModificationType.C_ADDS_TO_F,
    "f1.3.2.3": ModificationType.C_ADDS_TO_F,
    "f1.3.3.30": ModificationType.C_ADDS_TO_F,
    "f1.3.3.33": ModificationType.C_ADDS_TO_F,
    "f1.3.4.2": ModificationType.CHANGED_INTERVAL,
    "f1.4.3.1": ModificationType.CHANGED_INTERVAL,
    "f1.4.4.6": ModificationType.CHANGED_INTERVAL,
    "f1.4.5.14": ModificationType.CHANGED_INTERVAL,
    "f1.4.6.20": ModificationType.C_ADDS_TO_F,
    "f1.4.7.9": ModificationType.C_ADDS_TO_F,
}
