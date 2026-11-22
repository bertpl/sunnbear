"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``Fig. 3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Sabharwal2019Figure3(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x^9 - 8``; the formula's interval is ``[0.00, 1.50]``.

    In Figure 3's run of the false position method, the right endpoint stays fixed. The root is `2^(1/3)`.
    """

    number = (1, 2, 13, 3)
    name = "Figure 3"
    params = ()
    location_in_publication = "Fig. 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\tmp{u}^{9} - 8",
        interval="[0, 1.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return x**9 - 8

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-7.999243319357422),
        FormulaTestCase.value(params={}, x=1.05, c=0.25, expected=-7.970910654125263),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
