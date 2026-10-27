"""This module holds formula f1.99.4.4.7, the modified version of the published formula f1.4.4.7.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.4.7 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedBradie200621P67(Formula):
    """This formula is the modified version of formula f1.4.4.7, from Bradie (2006).

    The survey writes the source's function as ``13500*(1 + r/12)^36 + 250*((1 + r/12)^36 - 1)/(r/12) - 25000``, with
    the parameters initial investment, monthly deposit and goal: `13500, 250, 25000` (§2.1); `14000, 250, 25000` and
    `12500, 300, 25000` (2.1-19); the published interval is `[0.01, 0.10]` (§2.1).

    Unknown ``r``, the annual interest rate, compounded monthly over 3 years. ``f(0.01) = -1956.54``, ``f(0.10) =
    3645.91``; bisection to ``5E-6`` gives ``r = 0.0439395`` after 15 iterations. 2.5-20 asks the same for ``13000, 200,
    20000`` and ``13000, 250, 20000``, and gives no interval: since ``13000 + 36*200 = 20200`` already exceeds 20000,
    the goal is met even at ``r = 0``, and both roots are negative, about -0.0041 and -0.0405.

    At ``x = 0``, where the published function divides 0 by 0, the formula takes its limit, ``initial_investment +
    36*monthly_deposit - goal``.

    The formula holds only the test problem with ``initial_investment = 14000``, ``monthly_deposit = 250`` and ``goal =
    25000``, because the other parameter tuples of formula f1.4.4.7 satisfy the benchmark suite inclusion conditions.
    The formula computes the published function in the equivalent form ``expm1(36*log1p(x/12)) * (initial_investment +
    12*monthly_deposit/x) - (goal - initial_investment)``, on the published interval.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem with these values does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root, the published function rounds ``1 + x/12`` to float64, which drops the low bits of x, and then
    subtracts the goal, 25000, from a sum near 25000, so that f is exactly 0 at many x-values within about 1e-14 of the
    root.

    ``expm1(36*log1p(x/12))`` computes ``(1 + x/12)**36 - 1`` without rounding ``1 + x/12`` and without the subtraction
    of 1; the form still subtracts ``goal - initial_investment``, because f is by definition the savings after 3 years
    minus the goal, and the form moves the ``initial_investment`` term of the savings into that subtraction.

    The subtraction of ``goal - initial_investment`` still leaves f exactly 0 at 3 x-values, at most 2 float64 values
    away from the root, so that bisection can still stop early for some values of ``c``, but for none of the values of
    ``c`` of the shipped Monte Carlo tuple set.
    """

    number = (1, 99, 4, 4, 7)
    name = "§2.1 (p. 67)"
    param_names = ("initial_investment", "monthly_deposit", "goal")
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="§2.1 (p. 67); 2.1-19; 2.5-20",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, initial_investment: float, monthly_deposit: float, goal: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, in an equivalent form with ``expm1`` and ``log1p``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.09 * c
        if x == 0.0:
            # at x = 0, the factor ((1 + x/12)^36 - 1)/(x/12) takes its limit 36
            return initial_investment + 36.0 * monthly_deposit - goal
        else:
            growth_factor_minus_1 = math.expm1(36.0 * math.log1p(x / 12.0))
            return growth_factor_minus_1 * (initial_investment + 12.0 * monthly_deposit / x) - (
                goal - initial_investment
            )

    def interval_bounds(self, initial_investment: float, monthly_deposit: float, goal: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problem."""
        return (ParamTable(names=("initial_investment", "monthly_deposit", "goal"), rows=((14000.0, 250.0, 25000.0),)),)

    test_cases = (
        FormulaTestCase.interval_bounds(
            params={"initial_investment": 14000.0, "monthly_deposit": 250.0, "goal": 25000.0}, expected=(0.01, 0.1)
        ),
        FormulaTestCase.value(
            params={"initial_investment": 14000.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.037,
            c=0.25,
            expected=-1184.9991543651379,
        ),
        FormulaTestCase.value(
            params={"initial_investment": 14000.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.0,
            c=0.0,
            expected=-2000.0,
        ),
    )
