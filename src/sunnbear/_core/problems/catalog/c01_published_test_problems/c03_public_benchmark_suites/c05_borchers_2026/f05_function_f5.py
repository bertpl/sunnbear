"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF5(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x^2 - (1 - x)^9``; the formula's interval is ``[-1.4, 1]``.

    Printed root: `0.2592044937`
    """

    number = (1, 3, 5, 5)
    name = "Function f5"
    params = ()
    location_in_publication = "§5.6, f5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.4 \c"),),
        expression=r"\tmp{u}^{2} - \left(1 - \tmp{u}\right)^{9}",
        interval="[-1.4, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.4 * c
        return x**2 - (1 - x) ** 9

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.4, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.68, c=0.0, expected=-106.14406324783602),
        FormulaTestCase.value(params={}, x=-0.68, c=0.25, expected=-1663.3592428321983),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.4, 1.0)),
    )
