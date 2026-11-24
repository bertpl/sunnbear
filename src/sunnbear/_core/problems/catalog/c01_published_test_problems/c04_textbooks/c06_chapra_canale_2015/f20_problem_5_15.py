"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.15`` in the survey of published test problems.
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


class ChapraCanale2015Problem515(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``v = sqrt(2*g*H)*tanh(sqrt(2*g*H)/(2*L)*t)``, with the parameters `g =
    9.81` m/s^2, `L = 4` m, `t = 2.5` s, `v = 5` m/s; the formula's interval is ``[0, 2]``.

    Unknown `H`, the initial head (m) of the cylindrical tank of Fig. P5.15; `L` is the pipe's length and `t` the
    elapsed time. Graphically, and by bisection and false position to `es = 1%`.
    """

    number = (1, 4, 6, 20)
    name = "Problem 5.15"
    params = (
        FormulaParam("g", latex_symbol="g", meaning=r"The gravitational acceleration, in $\mathrm{m/s^2}$."),
        FormulaParam("L", latex_symbol="L", meaning="The pipe's length, in m."),
        FormulaParam("t", latex_symbol="t", meaning="The time since the tank started to drain, in s."),
        FormulaParam("v", latex_symbol="v", meaning="The target outflow velocity, in m/s."),
    )
    location_in_publication = "Prob. 5.15"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\param{v} - \sqrt{2 \param{g} \tmp{u}} \tanh{\left(\frac{\sqrt{2 \param{g} \tmp{u}}}{2 "
            r"\param{L}} \param{t} \right)}"
        ),
        interval="[0, 2]",
        summary=(
            "A target velocity minus the outflow velocity of a tank drained through a long pipe, as a decreasing "
            "function of the tank's initial head with 1 simple root."
        ),
        notes=(r"$\tmp{u}$ is the source's variable $H$, the tank's initial head, in m.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, g: float, L: float, t: float, v: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (v) - (math.sqrt(2 * g * x) * math.tanh(math.sqrt(2 * g * x) / (2 * L) * t))

    def interval_bounds(self, g: float, L: float, t: float, v: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("g", "L", "t", "v"), rows=((9.81, 4.0, 2.5, 5.0),), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.6, c=0.0, expected=2.2884942505464694
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.6, c=0.25, expected=4.423248410414592
        ),
        FormulaTestCase.interval_bounds(params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, expected=(0.0, 2.0)),
    )
