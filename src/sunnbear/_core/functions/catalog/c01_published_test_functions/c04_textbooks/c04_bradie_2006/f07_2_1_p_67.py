"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``§2.1 (p. 67); 2.1-19; 2.5-20`` in the survey of published test problems.
The survey gives this function as 1 expression that the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot translate: 5 sets of its constants, given in words as
initial investment, monthly deposit and goal. A person therefore writes this module, and a change of the formula's row
in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Bradie200621P67(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``13500*(1 + r/12)^36 + 250*((1 + r/12)^36 - 1)/(r/12) - 25000``, with
    the parameters initial investment, monthly deposit and goal: `13500, 250, 25000` (§2.1); `14000, 250, 25000` and
    `12500, 300, 25000` (2.1-19); `13000, 200, 20000` and `13000, 250, 20000` (2.5-20); the formula's interval is
    `[0.01, 0.10]` (§2.1).

    Unknown ``r``, the annual interest rate, compounded monthly over 3 years. ``f(0.01) = -1956.54``, ``f(0.10) =
    3645.91``; bisection to ``5E-6`` gives ``r = 0.0439395`` after 15 iterations.

    The parameters ``initial``, ``deposit`` and ``goal`` are the initial investment, the monthly deposit and the goal,
    and each set of them pairs with the row's only interval. At ``x = 0``, where the source's function divides 0 by 0,
    the formula takes its limit, ``initial + 36*deposit - goal``.
    """

    number = (1, 4, 4, 7)
    name = "§2.1 (p. 67)"
    param_names = ("initial", "deposit", "goal")
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="§2.1 (p. 67); 2.1-19; 2.5-20",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, initial: float, deposit: float, goal: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 0.09000000000000001 * c
        if x == 0.0:
            # at x = 0, the factor ((1 + x/12)^36 - 1)/(x/12) takes its limit 36
            return initial + 36.0 * deposit - goal
        else:
            growth = (1.0 + x / 12.0) ** 36
            return initial * growth + deposit * (growth - 1.0) / (x / 12.0) - goal

    def interval_bounds(self, initial: float, deposit: float, goal: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("initial", "deposit", "goal"),
                rows=(
                    (
                        13500.0,
                        250.0,
                        25000.0,
                    ),
                    (
                        14000.0,
                        250.0,
                        25000.0,
                    ),
                    (
                        12500.0,
                        300.0,
                        25000.0,
                    ),
                    (
                        13000.0,
                        200.0,
                        20000.0,
                    ),
                    (
                        13000.0,
                        250.0,
                        20000.0,
                    ),
                ),
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    cases = (
        FormulaTestCase.value(
            params={"initial": 13500.0, "deposit": 250.0, "goal": 25000.0}, x=0.037, c=0.0, expected=-414.7094119089419
        ),
        FormulaTestCase.value(
            params={"initial": 13500.0, "deposit": 250.0, "goal": 25000.0},
            x=0.037,
            c=0.25,
            expected=-1707.2154378902248,
            atol=2e-09,
        ),
        FormulaTestCase.value(
            params={"initial": 14000.0, "deposit": 250.0, "goal": 25000.0}, x=0.0865, c=0.0, expected=3364.9016342370865
        ),
        FormulaTestCase.value(
            params={"initial": 12500.0, "deposit": 300.0, "goal": 25000.0}, x=0.037, c=0.0, expected=368.69353168164696
        ),
        FormulaTestCase.value(
            params={"initial": 13000.0, "deposit": 200.0, "goal": 20000.0}, x=0.037, c=0.0, expected=2126.081492867649
        ),
        FormulaTestCase.value(
            params={"initial": 13000.0, "deposit": 250.0, "goal": 20000.0}, x=0.037, c=0.0, expected=4026.6885375467846
        ),
        FormulaTestCase.value(
            params={"initial": 13500.0, "deposit": 250.0, "goal": 25000.0}, x=0.0, c=0.0, expected=-2500.0
        ),
        FormulaTestCase.interval_bounds(
            params={"initial": 13500.0, "deposit": 250.0, "goal": 25000.0}, expected=(0.01, 0.1)
        ),
    )
