"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``9`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function9(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``(x - 1)^3 - 1``; the formula's interval is ``[1.5, 3]``.
    """

    number = (1, 2, 11, 6)
    name = "Function 9"
    params = ()
    location_in_publication = "Table 1, function 9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\left(\tmp{u} - 1\right)^{3} - 1",
        interval="[1.5, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return (x - 1) ** 3 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.5, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.95, c=0.0, expected=-0.1426250000000001),
        FormulaTestCase.value(params={}, x=1.95, c=0.25, expected=-0.8098906250000001),
        FormulaTestCase.interval_bounds(params={}, expected=(1.5, 3.0)),
    )
