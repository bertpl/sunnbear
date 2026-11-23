"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.2-7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise227(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^4 - 3*x^2 - 3``; the formula's interval is ``[1, 2]``.

    Fixed-point iteration from `p0 = 1` to `1E-2`.
    """

    number = (1, 4, 7, 26)
    name = "Exercise 2.2-7"
    params = ()
    location_in_publication = "Exercise 2.2-7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{4} - 3 \tmp{u}^{2} - 3",
        interval="[1, 2]",
        summary=(
            "A quartic that varies by only 0.25 over the lower 40% of the interval, with 1 simple root close to the "
            "upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**4 - 3 * x**2 - 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-5.2139),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-5.09199375),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
