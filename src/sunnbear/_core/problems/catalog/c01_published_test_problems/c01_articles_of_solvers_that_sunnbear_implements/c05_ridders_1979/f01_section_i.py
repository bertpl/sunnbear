"""This module holds a formula of Ridders (1979).

The formula comes from the row with the key ``I`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ridders1979SectionI(Formula):
    """This formula comes from Ridders (1979).

    The survey writes the source's function as ``x^3 - x - 5``; the formula's interval is ``[-1, 3]``.

    Printed root: `1.904160859...`.
    """

    number = (1, 1, 5, 1)
    name = "Section I"
    params = ()
    location_in_publication = "Section I"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\tmp{u}^{3} - \tmp{u} - 5",
        interval="[-1, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x**3 - x - 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.2, c=0.0, expected=-5.192),
        FormulaTestCase.value(params={}, x=0.2, c=0.25, expected=-4.712),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 3.0)),
    )
