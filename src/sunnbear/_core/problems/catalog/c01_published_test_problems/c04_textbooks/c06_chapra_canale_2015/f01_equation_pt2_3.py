"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``(PT2.3), (PT2.4); Ex. 5.1, 5.3–5.5; Fig. 5.1, 5.6, 5.7, 5.13; Prob. 5.14,
5.21, 5.23, 5.26, 7.20, 7.21`` in the survey of published test problems.
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


class ChapraCanale2015EquationPt23(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``(g*m/c)*(1 - exp(-(c/m)*t)) - v``, with the parameters given per
    interval, on `[12, 16]`, `[4, 20]`: `g = 9.81` m/s^2, `m = 68.1` kg, `v = 40` m/s, `t = 10` s (Ex. 5.1); on `[3,
    5]`: `m = 82`, `v = 36`, `t = 4` (Prob. 5.14); the formula's intervals are `[12, 16]` (Ex. 5.3, 5.5); `[3, 5]`
    (Prob. 5.14); `[4, 20]` (Fig. 5.1).

    Unknown `c`, the drag coefficient (kg/s) that gives a parachutist of mass `m` the velocity `v` after `t` seconds of
    free fall. Ex. 5.1 prints it with the values as (E5.1.1), `(668.06/c)*(1 - exp(-0.146843*c)) - 40`, and reads 14.75
    off a plot; Ex. 5.3 gives the root `14.8011`. By bisection to `es = 0.5%` (Ex. 5.3, 5.4) and by false position (Ex.
    5.5). Prob. 5.14 runs bisection to `es = 2%`; its interval holds the root, about 3.586. The other problems repeat
    Ex. 5.3–5.5 with the reader's programs; Prob. 5.26 stops by Eq. (5.5), with `Ea,d = 0.0001`.
    """

    number = (1, 4, 6, 1)
    name = "Equation (PT2.3)"
    params = (
        FormulaParam("g", latex_symbol="g", meaning=r"The gravitational acceleration, in $\mathrm{m/s^2}$."),
        FormulaParam("m", latex_symbol="m", meaning="The parachutist's mass, in kg."),
        FormulaParam("v", latex_symbol="v", meaning="The target velocity, in m/s."),
        FormulaParam("t", latex_symbol="t", meaning="The duration of the free fall, in s."),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = (
        "Eqs. (PT2.3), (PT2.4); Examples 5.1, 5.3–5.5; Fig. 5.1, 5.6, 5.7, 5.13; Prob. 5.14, 5.21, 5.23,"
        " 5.26, 7.20, 7.21"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\frac{\param{g} \param{m}}{\tmp{u}} \left(1 - e^{- \frac{\tmp{u}}{\param{m}} "
            r"\param{t}}\right) - \param{v}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A decreasing function with 1 simple root, the drag coefficient at which a falling parachutist reaches a "
            r"target velocity after $\param{t}$ seconds."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(
        x: float, c: float, g: float, m: float, v: float, t: float, a: float, b: float, c_scale: float
    ) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (g * m / x) * (1 - math.exp(-(x / m) * t)) - v

    def interval_bounds(
        self, g: float, m: float, v: float, t: float, a: float, b: float, c_scale: float
    ) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("g", "m", "v", "t", "a", "b", "c_scale"),
                rows=(
                    (9.81, 68.1, 40.0, 10.0, 12.0, 16.0, 4.0),
                    (9.81, 68.1, 40.0, 10.0, 4.0, 20.0, 16.0),
                    (9.81, 82.0, 36.0, 4.0, 3.0, 5.0, 2.0),
                ),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0},
            x=13.2,
            c=0.0,
            expected=3.325541753212046,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0},
            x=13.2,
            c=0.25,
            expected=5.630059449656643,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 4.0, "b": 20.0, "c_scale": 16.0},
            x=8.8,
            c=0.0,
            expected=15.064844887009704,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0},
            x=3.6,
            c=0.0,
            expected=-0.012330135450636158,
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0},
            expected=(12.0, 16.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 4.0, "b": 20.0, "c_scale": 16.0},
            expected=(4.0, 20.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0}, expected=(3.0, 5.0)
        ),
    )
