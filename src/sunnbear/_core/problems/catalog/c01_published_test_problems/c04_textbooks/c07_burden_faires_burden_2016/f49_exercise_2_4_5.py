"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise245(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(6*x) + 1.441*exp(2*x) - 2.079*exp(4*x) - 0.3330``; the formula's
    interval is ``[-1, 0]``.

    2.4-1(d) with its coefficients rounded to 4 digits, as the book says. Newton and the modified Newton method (2.13)
    to `1E-5`, compared with the results of 2.4-1(d) and of the book's "2(d)". That "2(d)" is most likely a slip for
    2.4-3(d), the modified Newton method on 2.4-1(d), because 2.4-2(d) is an unrelated function.
    """

    number = (1, 4, 7, 49)
    name = "Exercise 2.4-5"
    params = ()
    location_in_publication = "Exercise 2.4-5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{6 \tmp{u}} + 1.441 e^{2 \tmp{u}} - 2.079 e^{4 \tmp{u}} - 0.333",
        interval="[-1, 0]",
        summary=(
            r"The cube $(e^{2\x} - \ln(2))^3$ written out with coefficients rounded to 4 digits, so that the triple "
            r"root becomes 1 simple root with a slope of 0.002."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(6 * x) + 1.441 * math.exp(2 * x) - 2.079 * math.exp(4 * x) - 0.3330

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=-0.0890823183374955),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=-0.1606344889316799),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
