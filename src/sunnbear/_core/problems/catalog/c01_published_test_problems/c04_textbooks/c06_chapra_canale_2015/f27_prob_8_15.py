"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 8.15`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ChapraCanale2015Prob815(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``c = 10 - 20*(exp(-0.2*x) - exp(-0.75*x))``, with the parameters `c = 5`
    mg/L (a); the formula's interval is `[0, 2]` (a).

    The formula's parameter ``c_`` is the source's ``c``, renamed because the formula uses ``c`` for another value.

    Unknown `x`, the distance (km) downstream: (a) where `c` first falls to 5, to 1% error, which the book's hint places
    within 2 km; (b) where `c` is minimal, a root of `dc/dx`.
    """

    number = (1, 4, 6, 27)
    name = "Prob. 8.15"
    params = (FormulaParam("c_", latex_symbol="C"),)
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 8.15",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\param{c_} - \left(10 - 20 \left(e^{- 0.2 \tmp{u}} - e^{- 0.75 \tmp{u}}\right)\right)",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, c_: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (c_) - (10 - 20 * (math.exp(-0.2 * x) - math.exp(-0.75 * x)))

    def interval_bounds(self, c_: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("c_",), rows=((5.0,),), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"c_": 5.0}, x=0.6, c=0.0, expected=-0.014154298092315686),
        FormulaTestCase.value(params={"c_": 5.0}, x=0.6, c=0.25, expected=-3.950896260435952),
        FormulaTestCase.interval_bounds(params={"c_": 5.0}, expected=(0.0, 2.0)),
    )
