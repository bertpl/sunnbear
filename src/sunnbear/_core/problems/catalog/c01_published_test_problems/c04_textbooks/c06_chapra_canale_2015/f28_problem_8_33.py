"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 8.33`` in the survey of published test problems.
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


class ChapraCanale2015Problem833(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``1/Z = sqrt(1/R^2 + (omega*C - 1/(omega*L))^2)``, with the parameters `R
    = 225` ohm, `C = 0.6E-6` F, `L = 0.5` H, `Z = 75` ohm; the formula's interval is ``[1, 1000]``.

    Unknown `omega`, the angular frequency. Bisection and false position to `es = 0.1%`, with a graph to explain any
    difficulties.
    """

    number = (1, 4, 6, 28)
    name = "Problem 8.33"
    params = (
        FormulaParam("R", latex_symbol="R", meaning="The resistance, in ohms."),
        FormulaParam("C", latex_symbol="C", meaning="The capacitance, in farads."),
        FormulaParam("L", latex_symbol="L", meaning="The inductance, in henries."),
        FormulaParam("Z", latex_symbol="Z", meaning="The target impedance, in ohms."),
    )
    location_in_publication = "Prob. 8.33"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{\omega}", r"\x - 999 \c"),),
        expression=(
            r"\frac{1}{\param{Z}} - \sqrt{\frac{1}{\param{R}^{2}} + \left(\tmp{\omega} \param{C} - "
            r"\frac{1}{\tmp{\omega} \param{L}}\right)^{2}}"
        ),
        interval="[1, 1000]",
        summary=(
            "The impedance equation of a parallel RLC circuit in the angular frequency, with 1 simple root, right of "
            "which the function stays between 0 and 0.009."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, R: float, C: float, L: float, Z: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 999.0 * c
        return (1 / Z) - (math.sqrt(1 / R**2 + (x * C - 1 / (x * L)) ** 2))

    def interval_bounds(self, R: float, C: float, L: float, Z: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 1000.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("R", "C", "L", "Z"), rows=((225.0, 6e-07, 0.5, 75.0),), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"R": 225.0, "C": 6e-07, "L": 0.5, "Z": 75.0}, x=300.7, c=0.0, expected=0.005483276103780892
        ),
        FormulaTestCase.value(
            params={"R": 225.0, "C": 6e-07, "L": 0.5, "Z": 75.0}, x=300.7, c=0.25, expected=-0.026141265368335758
        ),
        FormulaTestCase.interval_bounds(params={"R": 225.0, "C": 6e-07, "L": 0.5, "Z": 75.0}, expected=(1.0, 1000.0)),
    )
