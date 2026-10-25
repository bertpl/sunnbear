"""This module lists the formulas of category 1 that have a modified version, and how each version is modified.

A formula of category 1 has a modified version when some of its published test problems do not satisfy the benchmark
suite inclusion conditions, the conditions on every test problem of a benchmark suite. The benchmark suite pipeline,
`sunnbear._core.benchmark.suites.pipeline`, checks these conditions.

The class docstring of `PublishedTestProblems` describes such a formula's parameter `modified`.

Such a formula's module is written by hand, starting from the module that the generator writes for the formula when the
formula is absent from `MODIFIED_FORMULAS`.
"""

from enum import StrEnum


# ==================================================================================================
#  ModificationType
# ==================================================================================================
class ModificationType(StrEnum):
    """A `ModificationType` names how test problems with ``modified = n`` differ from those with ``modified = n - 1``.

    The value of ``modified`` is the level of modification; level 0 holds the published test problems. Every type except
    `CANCELLATION_FREE_FORM` applies only at level 1, so its comment compares with the published test problem.
    """

    # The modified function adds the parameter c of category 1 to the published function's value, on the published
    # interval, and does not shift x.
    C_ADDS_TO_F = "c_adds_to_f"
    # The modified function has its own interval; the formula's docstring states the new interval and why the interval
    # changed. One bound of the published interval, or both, moves in 1 of 2 ways:
    # - away from the pole, jump, root or other value of x at which the published function fails;
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
    # The modified function writes the function of the level below in a form whose terms do not cancel in float64: for
    # example, (x - 1)**3 in place of x**3 - 3*x**2 + 3*x - 1, whose terms cancel near the root at 1. At level 1, the
    # level below is the published function.
    # The modified function keeps the interval of the level below, and applies c:
    # - at level 1, by the rule of category 1;
    # - at higher levels, as the level below does.
    CANCELLATION_FREE_FORM = "cancellation_free_form"

    @property
    def is_c_scale_shift_kept(self) -> bool:
        """Return whether the type keeps the rule of category 1, by which ``c`` shifts x by ``c_scale*c``.

        `CANCELLATION_FREE_FORM` returns True because it applies ``c`` as the level below does, so a test problem keeps
        the rule only where this property is True for every level up to its own.
        """
        return self in (
            ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,
            ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,
            ModificationType.CANCELLATION_FREE_FORM,
        )


# MODIFIED_FORMULAS holds, for each formula of category 1 that has the parameter `modified`, the type of modification of
# each level, starting at `modified = 1`. Each level applies the modifications of the levels below it plus its own type.
MODIFIED_FORMULAS = {
    "f1.1.2.4": (ModificationType.C_ADDS_TO_F,),
    "f1.1.5.3": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.1.6.3": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.7.2": (ModificationType.C_SCALES_X,),
    "f1.1.7.8": (ModificationType.C_SCALES_X,),
    "f1.1.7.9": (ModificationType.C_SCALES_X,),
    "f1.1.8.1": (ModificationType.C_SCALES_X,),
    "f1.1.9.15": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.12.1": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.1.12.2": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.1.12.4": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.13.4": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.13.5": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.13.19": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.1.13.21": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.4.2": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.9.4": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.2.9.6": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.2.13.8": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.13.9": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.15.1": (ModificationType.C_ADDS_TO_F,),
    "f1.2.15.2": (ModificationType.C_ADDS_TO_F,),
    "f1.2.18.5": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.18.6": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.18.14": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.2.18.20": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.1.4": (ModificationType.C_SCALES_X,),
    "f1.3.1.6": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.1.17": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.3.2.3": (ModificationType.C_ADDS_TO_F,),
    "f1.3.2.5": (ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0, ModificationType.CANCELLATION_FREE_FORM),
    "f1.3.3.30": (ModificationType.C_ADDS_TO_F,),
    "f1.3.3.33": (ModificationType.C_ADDS_TO_F,),
    "f1.3.3.41": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.3.4.2": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.5.12": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.3.5.13": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.6.2": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.6.3": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.3.6.4": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.1.2": (ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0, ModificationType.CANCELLATION_FREE_FORM),
    "f1.4.1.6": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.1.8": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.2.1": (ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0,),
    "f1.4.2.5": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.3.1": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.3.2": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.3.5": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.3.6": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.3.14": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.3.15": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.4.6": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.4.28": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.5.8": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.5.14": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.5.15": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.5.20": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.5.21": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.5.22": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.5.23": (ModificationType.C_SHIFTS_X_ON_INTERVAL_NEAR_0, ModificationType.CANCELLATION_FREE_FORM),
    "f1.4.6.1": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.6.2": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.6.20": (ModificationType.C_ADDS_TO_F,),
    "f1.4.7.4": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.7.9": (ModificationType.C_ADDS_TO_F,),
    "f1.4.7.19": (ModificationType.C_SHIFTS_X_ON_NEW_INTERVAL,),
    "f1.4.7.43": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.7.47": (ModificationType.CANCELLATION_FREE_FORM,),
    "f1.4.7.48": (ModificationType.CANCELLATION_FREE_FORM,),
}
