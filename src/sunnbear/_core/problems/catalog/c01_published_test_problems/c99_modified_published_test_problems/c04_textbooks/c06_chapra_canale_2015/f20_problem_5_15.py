"""This module holds formula f1.99.4.6.20, the modified version of the published formula f1.4.6.20.

A change of formula f1.4.6.20 may need a matching change of this module.
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


class ModifiedChapraCanale2015Problem515(Formula):
    """This formula is the modified version of formula f1.4.6.20, from Chapra, Canale (2015).

    The survey writes the source's function as ``v = sqrt(2*g*H)*tanh(sqrt(2*g*H)/(2*L)*t)``, with the parameters `g =
    9.81` m/s^2, `L = 4` m, `t = 2.5` s, `v = 5` m/s; the published interval is ``[0, 2]``.

    Unknown `H`, the initial head (m) of the cylindrical tank of Fig. P5.15; `L` is the pipe's length and `t` the
    elapsed time. Graphically, and by bisection and false position to `es = 1%`.

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because a shift along x by
    any ``c > 0`` evaluates ``sqrt(2*g*x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 99, 4, 6, 20)
    name = "Problem 5.15"
    params = (
        FormulaParam("g", latex_symbol="g", meaning=r"The gravitational acceleration, in $\mathrm{m/s^2}$."),
        FormulaParam("L", latex_symbol="L", meaning="The pipe's length, in m."),
        FormulaParam("t", latex_symbol="t", meaning="The time since the tank started to drain, in s."),
        FormulaParam("v", latex_symbol="v", meaning="The target outflow velocity, in m/s."),
    )
    location_in_publication = "Prob. 5.15"
    presentation = FormulaPresentation(
        expression=(
            r"\param{v} - \sqrt{2 \param{g} \x} \tanh{\left(\frac{\sqrt{2 \param{g} \x}}{2 \param{L}} "
            r"\param{t} \right)} + \c"
        ),
        interval="[0, 2]",
        summary=(
            "A target velocity minus the outflow velocity of a tank drained through a long pipe, as a decreasing "
            "function of the tank's initial water height with 1 simple root."
        ),
        notes=(
            (
                r"$\c$ shifts the function along the y-axis, not along x as for the published test "
                r"problem, because a shift along x by any $\c > 0$ evaluates $\sqrt{2 \param{g} \x}$ left "
                "of 0, outside its domain."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, g: float, L: float, t: float, v: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return (v) - (math.sqrt(2 * g * x) * math.tanh(math.sqrt(2 * g * x) / (2 * L) * t)) + c

    def interval_bounds(self, g: float, L: float, t: float, v: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problem."""
        return (
            ParamTable(
                names=("g", "L", "t", "v"), rows=((9.81, 4.0, 2.5, 5.0),), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.6, c=0.25, expected=2.5384942505464694
        ),
        FormulaTestCase.value(params={"g": 9.81, "L": 4.0, "t": 2.5, "v": 5.0}, x=0.0, c=-0.25, expected=4.75),
    )
