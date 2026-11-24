"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 8.15`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ChapraCanale2015Problem815(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``c = 10 - 20*(exp(-0.2*x) - exp(-0.75*x))``, with the parameters `c = 5`
    mg/L (a); the formula's interval is `[0, 2]` (a).

    Unknown `x`, the distance (km) downstream: (a) where `c` first falls to 5, to 1% error, which the book's hint places
    within 2 km; (b) where `c` is minimal, a root of `dc/dx`.
    """

    number = (1, 4, 6, 27)
    name = "Problem 8.15"
    params = (
        FormulaParam(
            "Ct", latex_symbol=r"C_{\mathrm{t}}", meaning="The target concentration of dissolved oxygen, in mg/L."
        ),
    )
    location_in_publication = "Prob. 8.15"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\param{Ct} - \left(10 - 20 \left(e^{- 0.2 \tmp{u}} - e^{- 0.75 \tmp{u}}\right)\right)",
        interval="[0, 2]",
        summary=(
            "A target concentration minus the oxygen sag curve downstream of a sewage discharge, increasing through 1 "
            "simple root to a maximum 1.8 above that root."
        ),
        notes=(r"$\param{Ct}$ is the source's parameter $c$.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, Ct: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (Ct) - (10 - 20 * (math.exp(-0.2 * x) - math.exp(-0.75 * x)))

    def interval_bounds(self, Ct: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("Ct",), rows=((5.0,),), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"Ct": 5.0}, x=0.6, c=0.0, expected=-0.014154298092315686),
        FormulaTestCase.value(params={"Ct": 5.0}, x=0.6, c=0.25, expected=-3.950896260435952),
        FormulaTestCase.interval_bounds(params={"Ct": 5.0}, expected=(0.0, 2.0)),
    )
