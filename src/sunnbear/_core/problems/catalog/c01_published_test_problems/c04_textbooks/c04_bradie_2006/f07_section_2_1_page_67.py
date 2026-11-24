"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``§2.1 (p. 67); 2.1-19; 2.5-20`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Bradie2006Section21Page67(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``13500*(1 + r/12)^36 + 250*((1 + r/12)^36 - 1)/(r/12) - 25000``, with
    the parameters initial investment, monthly deposit and goal: `13500, 250, 25000` (§2.1); `14000, 250, 25000` and
    `12500, 300, 25000` (2.1-19); the formula's interval is `[0.01, 0.10]` (§2.1).

    Unknown ``r``, the annual interest rate, compounded monthly over 3 years. ``f(0.01) = -1956.54``, ``f(0.10) =
    3645.91``; bisection to ``5E-6`` gives ``r = 0.0439395`` after 15 iterations. 2.5-20 asks the same for ``13000, 200,
    20000`` and ``13000, 250, 20000``, and gives no interval: since ``13000 + 36*200 = 20200`` already exceeds 20000,
    the goal is met even at ``r = 0``, and both roots are negative, about -0.0041 and -0.0405.

    The parameters ``initial_investment``, ``monthly_deposit`` and ``goal`` are the initial investment, the monthly
    deposit and the goal, and each set of them pairs with the row's only interval. At ``x = 0``, where the source's
    function divides 0 by 0, the formula takes its limit, ``initial_investment + 36*monthly_deposit - goal``.
    """

    number = (1, 4, 4, 7)
    name = "Section 2.1 (page 67)"
    params = (
        FormulaParam("initial_investment", latex_symbol=r"\mathit{investment}"),
        FormulaParam("monthly_deposit", latex_symbol=r"\mathit{monthly\ deposit}"),
        FormulaParam("goal", latex_symbol=r"\mathit{goal}"),
    )
    location_in_publication = "§2.1 (p. 67); Exercises 2.1-19, 2.5-20"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 0.09 \c"),
            (r"\tmp{g}", r"\left(1 + \frac{\tmp{u}}{12}\right)^{36}"),
        ),
        expression=(
            r"\begin{cases} "
            r"\param{initial_investment} + 36 \param{monthly_deposit} - \param{goal} & \text{if } \tmp{u} = 0 \\ "
            r"\param{initial_investment} \tmp{g} + \param{monthly_deposit} \frac{\tmp{g} - 1}{\tmp{u}/12} "
            r"- \param{goal} "
            r"& \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0.01, 0.1]",
        summary=(
            "A savings balance minus a goal as a slightly convex function of the annual interest rate, with 1 simple "
            "root in the lower half of the interval."
        ),
        notes=(r"$\tmp{u}$ is the source's variable $r$, the annual interest rate.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, initial_investment: float, monthly_deposit: float, goal: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.09 * c
        if x == 0.0:
            # at x = 0, the factor ((1 + x/12)^36 - 1)/(x/12) takes its limit 36
            return initial_investment + 36.0 * monthly_deposit - goal
        else:
            growth_factor = (1.0 + x / 12.0) ** 36
            return initial_investment * growth_factor + monthly_deposit * (growth_factor - 1.0) / (x / 12.0) - goal

    def interval_bounds(self, initial_investment: float, monthly_deposit: float, goal: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("initial_investment", "monthly_deposit", "goal"),
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
                ),
                summary="The published parameter values.",
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(
            params={"initial_investment": 13500.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.037,
            c=0.0,
            expected=-414.7094119089419,
        ),
        FormulaTestCase.value(
            params={"initial_investment": 13500.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.037,
            c=0.25,
            expected=-1707.2154378902246,
            atol=2e-09,
        ),
        FormulaTestCase.value(
            params={"initial_investment": 14000.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.0865,
            c=0.0,
            expected=3364.9016342370865,
        ),
        FormulaTestCase.value(
            params={"initial_investment": 12500.0, "monthly_deposit": 300.0, "goal": 25000.0},
            x=0.037,
            c=0.0,
            expected=368.69353168164696,
        ),
        FormulaTestCase.value(
            params={"initial_investment": 13500.0, "monthly_deposit": 250.0, "goal": 25000.0},
            x=0.0,
            c=0.0,
            expected=-2500.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"initial_investment": 13500.0, "monthly_deposit": 250.0, "goal": 25000.0}, expected=(0.01, 0.1)
        ),
    )
