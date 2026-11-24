"""This module holds a formula of Alefeld, Potra (1992).

The formula comes from the row with the key ``3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class AlefeldPotra1992Problem3(Formula):
    """This formula comes from Alefeld, Potra (1992).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's interval is ``[0.1, 1]``.
    """

    number = (1, 2, 3, 3)
    name = "Problem 3"
    params = ()
    location_in_publication = "Table 1, problem 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.9 \c"),),
        expression=r"11 \tmp{u}^{11} - 1",
        interval="[0.1, 1]",
        summary=(
            "An 11th power minus 1, with 1 root, steep toward the upper bound and within 0.01 of $-1$ at every point of"
            " the interval that lies more than 0.28 below that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.9 * c
        return 11 * x**11 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.37, c=0.0, expected=-0.9998042906160426),
        FormulaTestCase.value(params={}, x=0.37, c=0.25, expected=-0.9999999934469919),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 1.0)),
    )
