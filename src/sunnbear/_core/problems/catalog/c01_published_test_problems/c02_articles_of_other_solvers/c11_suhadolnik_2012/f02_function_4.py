"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function4(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's interval is ``[.5, 1]``.
    """

    number = (1, 2, 11, 2)
    name = "Function 4"
    params = ()
    location_in_publication = "Table 1, function 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"11 \tmp{u}^{11} - 1",
        interval="[0.5, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return 11 * x**11 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.65, c=0.0, expected=-0.9037413850859033),
        FormulaTestCase.value(params={}, x=0.65, c=0.25, expected=-0.9908136069632425),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.0)),
    )
