"""This module holds formula f1.99.4.4.7, the modified version of the published formula f1.4.4.7.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.4.7 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# ROOT is the float64 nearest to the published function's root, with initial investment 14000, monthly deposit 250 and
# goal 25000.
ROOT = 0.03462803634918049
# GROWTH_AT_ROOT is ``(1 + ROOT/12)**36 - 1``, and VALUE_AT_ROOT is the published function's value at ROOT; both are
# computed with mpmath and rounded to float64.
GROWTH_AT_ROOT = 0.10930590526391942
VALUE_AT_ROOT = -1.750340631812349e-13


class ModifiedBradie200621P67(Formula):
    """This formula is the modified version of formula f1.4.4.7, from Bradie (2006).

    The survey writes the source's function as ``13500*(1 + r/12)^36 + 250*((1 + r/12)^36 - 1)/(r/12) - 25000``, with
    the parameters initial investment, monthly deposit and goal: `13500, 250, 25000` (§2.1); `14000, 250, 25000` and
    `12500, 300, 25000` (2.1-19); the published interval is `[0.01, 0.10]` (§2.1).

    Unknown ``r``, the annual interest rate, compounded monthly over 3 years. ``f(0.01) = -1956.54``, ``f(0.10) =
    3645.91``; bisection to ``5E-6`` gives ``r = 0.0439395`` after 15 iterations. 2.5-20 asks the same for ``13000, 200,
    20000`` and ``13000, 250, 20000``, and gives no interval: since ``13000 + 36*200 = 20200`` already exceeds 20000,
    the goal is met even at ``r = 0``, and both roots are negative, about -0.0041 and -0.0405.

    The formula holds only the test problem with initial investment 14000, monthly deposit 250 and goal 25000, and uses
    these values as constants in the function, because `ROOT`, `GROWTH_AT_ROOT` and `VALUE_AT_ROOT` hold for these
    values only.

    The formula computes the published function as its value at `ROOT`, the float64 nearest to the root, plus the change
    of the function from `ROOT` to x, on the published interval. At ``x = 0``, where the published function divides 0 by
    0, the formula takes its limit, -2000.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem with these values does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root, f subtracts the goal, 25000, from a sum near 25000, so that f is exactly 0 at many x-values within
    about 1e-14 of the root.

    The change of the published function from `ROOT` to x is ``(1 + GROWTH_AT_ROOT)*relative_growth_factor_change*(14000
    + 12*250/x) - GROWTH_AT_ROOT*12*250*t/(x*ROOT)``, with ``t = x - ROOT``. ``relative_growth_factor_change =
    expm1(36*log1p(t/(12 + ROOT)))`` is the relative change of the growth factor ``(1 + x/12)**36`` from `ROOT` to x,
    since ``(1 + x/12)**36`` equals ``(1 + ROOT/12)**36 * (1 + t/(12 + ROOT))**36``.

    Near the root, both terms of the change are proportional to ``t``, so the rounding error of f is a few float64
    spacings at the value of f, not at 25000, and f is exactly 0 at no x-value near the root.

    Rounding `ROOT`, `GROWTH_AT_ROOT` and `VALUE_AT_ROOT` to float64 moves the root by a negligible fraction of the
    float64 spacing at the root.
    """

    number = (1, 99, 4, 4, 7)
    name = "§2.1 (p. 67)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="§2.1 (p. 67); 2.1-19; 2.5-20",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as its value at `ROOT` plus its change from `ROOT`.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.09 * c
        if x == 0.0:
            # at x = 0, the published function divides 0 by 0; the formula takes its limit
            return 14000.0 + 36.0 * 250.0 - 25000.0
        else:
            t = x - ROOT
            relative_growth_factor_change = math.expm1(36.0 * math.log1p(t / (12.0 + ROOT)))
            return (
                VALUE_AT_ROOT
                + (1.0 + GROWTH_AT_ROOT) * relative_growth_factor_change * (14000.0 + 12.0 * 250.0 / x)
                - GROWTH_AT_ROOT * 12.0 * 250.0 * t / (x * ROOT)
            )

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 0.1)),
        FormulaTestCase.value(params={}, x=0.037, c=0.25, expected=-1184.9991543651379),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=-2000.0),
    )
