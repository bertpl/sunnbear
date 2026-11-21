"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``22`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202622(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^3 - 3*x^2 - 4*x + 13``; the formula's interval is ``[-3, -2]``.
    """

    number = (1, 2, 18, 7)
    name = "22"
    params = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="dataset.json, problem 22",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"\tmp{u}^{3} - 3 \tmp{u}^{2} - 4 \tmp{u} + 13",
        interval="[-3, -2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 3 * x**2 - 4 * x + 13

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, -2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-2.7, c=0.0, expected=-17.753000000000007),
        FormulaTestCase.value(params={}, x=-2.7, c=0.25, expected=-26.979875000000007),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, -2.0)),
    )
