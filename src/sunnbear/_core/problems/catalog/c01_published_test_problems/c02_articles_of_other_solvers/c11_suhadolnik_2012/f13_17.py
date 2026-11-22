"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``17`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik201217(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``x^3``; the formula's interval is ``[-0.5, 1/3]``.

    Section 4 names examples 17 and 18 as cases where `f'(x*) = 0`, on which the methods may converge slowly.
    """

    number = (1, 2, 11, 13)
    name = "17"
    params = ()
    location_in_publication = "Table 1, function 17"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.833 \c"),),
        expression=r"\tmp{u}^{3}",
        interval=r"\left[-0.5, \frac{1}{3}\right]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.833 * c
        return x**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 0.3333333333333333)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.25, c=0.0, expected=-0.015625),
        FormulaTestCase.value(params={}, x=-0.25, c=0.25, expected=-0.096229320890625),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 0.3333333333333333)),
    )
