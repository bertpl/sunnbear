"""This module lists the formulas of category 1 that have a modified version, and how each version is modified.

A formula of category 1 has a modified version when some of its published test functions do not satisfy the benchmark
suite inclusion conditions, which the benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`, checks. The
class docstring of `PublishedTestFunctions` describes such a formula's parameter `modified`.

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
    # The modified function has its own interval; the formula's docstring states the new interval and why the interval
    # changed. One bound of the published interval, or both, moves in 1 of 2 ways:
    # - away from the pole, jump, root or other value of x at which the published test function fails;
    # - past a root, so that the interval holds an odd number of roots.
    # c shifts x by the rule of category 1, with c_scale the rounded width of the new interval.
    C_SHIFTS_X_ON_NEW_INTERVAL = "c_shifts_x_on_new_interval"
    # The modified function keeps the published interval [a, b] and evaluates the published function at
    # x*exp(-c*ln(b/a)): c scales x, so that the root moves by the factor (b/a)**c and never reaches 0.
    C_SCALES_X = "c_scales_x"
    # The modified function evaluates the published function at x + s, where the formula's docstring states the
    # constant s. The modified function has its own interval, at or around 0, so that the interval is no longer narrow
    # next to its distance from 0, or holds 1 root of a V-shaped function; c shifts x by the rule of category 1, with
    # c_scale the rounded width of the new interval.
    C_SHIFTS_X_ON_INTERVAL_NEAR_0 = "c_shifts_x_on_interval_near_0"

    @property
    def is_x_shifted_by_c_scale(self) -> bool:
        """Return whether the modified function shifts x by ``c_scale*c``, the rule of category 1."""
        return self in (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL, ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0)


# MODIFIED_FORMULAS holds the type of modification of each formula of category 1 that has the parameter `modified`.
MODIFIED_FORMULAS = {
    "f1.1.2.4": ModificationType.C_ADDS_TO_F,
    "f1.1.5.3": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.1.7.2": ModificationType.C_SCALES_X,
    "f1.1.7.8": ModificationType.C_SCALES_X,
    "f1.1.7.9": ModificationType.C_SCALES_X,
    "f1.1.8.1": ModificationType.C_SCALES_X,
    "f1.1.12.1": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.1.12.2": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.1.13.21": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.4.2": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.13.8": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.13.9": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.15.1": ModificationType.C_ADDS_TO_F,
    "f1.2.15.2": ModificationType.C_ADDS_TO_F,
    "f1.2.18.5": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.18.6": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.18.14": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.2.18.20": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.1.4": ModificationType.C_SCALES_X,
    "f1.3.1.6": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.2.3": ModificationType.C_ADDS_TO_F,
    "f1.3.2.5": ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,
    "f1.3.3.30": ModificationType.C_ADDS_TO_F,
    "f1.3.3.33": ModificationType.C_ADDS_TO_F,
    "f1.3.4.2": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.5.13": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.6.2": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.6.3": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.3.6.4": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.1.2": ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,
    "f1.4.1.8": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.2.1": ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,
    "f1.4.2.5": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.3.1": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.3.5": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.3.6": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.3.15": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.4.6": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.8": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.14": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.15": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.20": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.21": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.5.23": ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,
    "f1.4.6.2": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.6.20": ModificationType.C_ADDS_TO_F,
    "f1.4.7.4": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
    "f1.4.7.9": ModificationType.C_ADDS_TO_F,
    "f1.4.7.19": ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
}
