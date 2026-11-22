"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.11.4, Fig. 3.12`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Figure312(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^5 - (5/2)*x^4 + (5/2)*x^3 - (5/4)*x^2 + (5/16)*x - 1/32``; the
    formula's interval is ``[0.45, 0.55]``.

    Printed also as `(x - 1/2)^5`. Evaluated in floating point at 8000 points of the interval, its values form a band
    around 0.
    """

    number = (1, 4, 5, 22)
    name = "Figure 3.12"
    params = ()
    location_in_publication = "§3.11.4, Fig. 3.12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.1 \c"),),
        expression=(
            r"\tmp{u}^{5} - \frac{5 \tmp{u}^{4}}{2} + \frac{5 \tmp{u}^{3}}{2} - \frac{5 \tmp{u}^{2}}{4} "
            r"+ \frac{5 \tmp{u}}{16} - \frac{1}{32}"
        ),
        interval="[0.45, 0.55]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.1 * c
        return x**5 - (5 / 2) * x**4 + (5 / 2) * x**3 - (5 / 4) * x**2 + (5 / 16) * x - 1 / 32

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.45, 0.55)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.48, c=0.0, expected=-3.200000000000014e-09),
        FormulaTestCase.value(params={}, x=0.48, c=0.25, expected=-1.8452812500000082e-07),
        FormulaTestCase.interval_bounds(params={}, expected=(0.45, 0.55)),
    )
