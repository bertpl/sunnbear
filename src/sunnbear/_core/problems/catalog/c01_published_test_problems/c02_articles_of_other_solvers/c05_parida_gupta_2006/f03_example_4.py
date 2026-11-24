"""This module holds a formula of Parida, Gupta (2006).

The formula comes from the row with the key ``4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ParidaGupta2006Example4(Formula):
    """This formula comes from Parida, Gupta (2006).

    The survey writes the source's function as ``x^6 - 36*x^5 + 450*x^4 - 2400*x^3 + 5400*x^2 - 4320*x + 720``; the
    formula's interval is ``[10, 22]``.

    `x0 = 22`. Root 15.9828739, the largest root of the polynomial.
    """

    number = (1, 2, 5, 3)
    name = "Example 4"
    params = ()
    location_in_publication = "Example 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 12 \c"),),
        expression=(
            r"\tmp{u}^{6} - 36 \tmp{u}^{5} + 450 \tmp{u}^{4} - 2400 \tmp{u}^{3} + 5400 \tmp{u}^{2} - "
            r"4320 \tmp{u} + 720"
        ),
        interval="[10, 22]",
        summary=(
            r"The Laguerre polynomial of degree 6, scaled by 720, with only the largest root on the interval and a "
            r"minimum 1.7 below that root, of about $-1.3 \cdot 10^{5}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 12.0 * c
        return x**6 - 36 * x**5 + 450 * x**4 - 2400 * x**3 + 5400 * x**2 - 4320 * x + 720

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (10.0, 22.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=13.6, c=0.0, expected=-123547.495424),
        FormulaTestCase.value(params={}, x=13.6, c=0.25, expected=-14713.047103999992),
        FormulaTestCase.interval_bounds(params={}, expected=(10.0, 22.0)),
    )
