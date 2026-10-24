"""This module lists the formulas of category 1 that have a modified version, and how each version is modified.

A formula of category 1 has a modified version when some of its published test functions fail the validation of the
benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`. An example is a function that is not defined
left of its interval, where every shift along x takes the interval's lower bound outside the function's domain. Such a
formula has the parameter `modified`: 0 for its published test functions, and 1 for modified versions of those that
fail. Its module is written by hand, starting from its generated module.
"""

from enum import StrEnum


# ==================================================================================================
#  Modification
# ==================================================================================================
class Modification(StrEnum):
    """A `Modification` names how a formula's test functions with ``modified = 1`` differ from its published ones."""

    # c adds to the published function's value, on the published interval, and x is not shifted.
    C_ADDS_TO_F = "c_adds_to_f"


# MODIFIED_FORMULAS holds the modification of each formula of category 1 that has the parameter `modified`.
MODIFIED_FORMULAS = {
    "f1.1.2.4": Modification.C_ADDS_TO_F,
    "f1.2.15.1": Modification.C_ADDS_TO_F,
    "f1.2.15.2": Modification.C_ADDS_TO_F,
    "f1.3.2.3": Modification.C_ADDS_TO_F,
    "f1.3.3.30": Modification.C_ADDS_TO_F,
    "f1.3.3.33": Modification.C_ADDS_TO_F,
    "f1.4.6.20": Modification.C_ADDS_TO_F,
    "f1.4.7.9": Modification.C_ADDS_TO_F,
}
