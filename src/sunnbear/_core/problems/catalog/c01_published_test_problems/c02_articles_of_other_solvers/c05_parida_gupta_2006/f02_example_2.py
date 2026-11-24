"""This module holds a formula of Parida, Gupta (2006).

The formula comes from the row with the key ``2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ParidaGupta2006Example2(Formula):
    """This formula comes from Parida, Gupta (2006).

    The survey writes the source's function as ``3*x^2 - 11.12*x + 9.1389``; the formula's interval is ``[-30, 2]``.

    `x0 = -30`. Root 1.23; the other root, about 2.4767, lies outside the interval.
    """

    number = (1, 2, 5, 2)
    name = "Example 2"
    params = ()
    location_in_publication = "Example 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 32 \c"),),
        expression=r"3 \tmp{u}^{2} - 11.12 \tmp{u} + 9.1389",
        interval="[-30, 2]",
        summary=(
            "A parabola whose 2 roots lie 1.25 apart near the upper bound of a wide interval, with only the lower root "
            "on the interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 32.0 * c
        return 3 * x**2 - 11.12 * x + 9.1389

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-30.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-20.4, c=0.0, expected=1484.4669),
        FormulaTestCase.value(params={}, x=-20.4, c=0.25, expected=2744.6268999999998),
        FormulaTestCase.interval_bounds(params={}, expected=(-30.0, 2.0)),
    )
