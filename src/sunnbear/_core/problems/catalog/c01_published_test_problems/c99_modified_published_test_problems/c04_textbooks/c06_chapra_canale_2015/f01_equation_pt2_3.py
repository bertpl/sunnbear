"""This module holds formula f1.99.4.6.1, the modified version of the published formula f1.4.6.1.

A change of formula f1.4.6.1 may need a matching change of this module.
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


class ModifiedChapraCanale2015EquationPt23(Formula):
    """This formula is the modified version of formula f1.4.6.1, from Chapra, Canale (2015).

    The survey writes the source's function as ``(g*m/c)*(1 - exp(-(c/m)*t)) - v``, with the parameters given per
    interval, on `[12, 16]`, `[4, 20]`: `g = 9.81` m/s^2, `m = 68.1` kg, `v = 40` m/s, `t = 10` s (Ex. 5.1); on `[3,
    5]`: `m = 82`, `v = 36`, `t = 4` (Prob. 5.14); the published intervals are `[12, 16]` (Ex. 5.3, 5.5); `[3, 5]`
    (Prob. 5.14); `[4, 20]` (Fig. 5.1).

    Unknown `c`, the drag coefficient (kg/s) that gives a parachutist of mass `m` the velocity `v` after `t` seconds of
    free fall. Ex. 5.1 prints it with the values as (E5.1.1), `(668.06/c)*(1 - exp(-0.146843*c)) - 40`, and reads 14.75
    off a plot; Ex. 5.3 gives the root `14.8011`. By bisection to `es = 0.5%` (Ex. 5.3, 5.4) and by false position (Ex.
    5.5). Prob. 5.14 runs bisection to `es = 2%`; its interval holds the root, about 3.586. The other problems repeat
    Ex. 5.3–5.5 with the reader's programs; Prob. 5.26 stops by Eq. (5.5), with `Ea,d = 0.0001`.

    The formula holds only the test problem on ``[3, 5]``. The formula computes the published function in the equivalent
    form ``(g*m/x)*(-expm1(-(x/m)*t)) - v``, on that interval; ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the published interval.

    The published test problem on ``[3, 5]`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 3e-14 of
    the root.

    ``-expm1(-(x/m)*t)`` computes ``1 - exp(-(x/m)*t)`` without the subtraction; the subtraction of ``v`` stays, because
    it is the function's definition: the velocity after ``t`` seconds minus ``v``.

    The subtraction of ``v`` still leaves f exactly 0 at x-values up to about 30 float64 values away from the root,
    so that bisection can still stop early for some values of ``c``. The formula modifies the function no further,
    because no equivalent form removes the subtraction of ``v``.
    """

    number = (1, 99, 4, 6, 1)
    name = "Equation (PT2.3)"
    params = (
        FormulaParam("g", latex_symbol="g", meaning=r"The gravitational acceleration, in $\mathrm{m/s^2}$."),
        FormulaParam("m", latex_symbol="m", meaning="The parachutist's mass, in kg."),
        FormulaParam("v", latex_symbol="v", meaning="The target velocity, in m/s."),
        FormulaParam("t", latex_symbol="t", meaning="The duration of the free fall, in s."),
    )
    location_in_publication = (
        "Eqs. (PT2.3), (PT2.4); Examples 5.1, 5.3–5.5; Fig. 5.1, 5.6, 5.7, 5.13; Prob. 5.14, 5.21, 5.23,"
        " 5.26, 7.20, 7.21"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\frac{\param{g} \param{m}}{\tmp{u}} \left(-\operatorname{expm1}\left(- "
            r"\frac{\tmp{u}}{\param{m}} \param{t}\right)\right) - \param{v}"
        ),
        interval="[3, 5]",
        summary=(
            "A decreasing function with 1 simple root, the drag coefficient at which a falling parachutist "
            r"reaches a target velocity after $\param{t}$ seconds."
        ),
        notes=(
            r"$\tmp{u}$ is the source's $c$, the drag coefficient, in kg/s.",
            (
                r"The expression equals the published function, $$\frac{\param{g} \param{m}}{\tmp{u}} "
                r"\left(1 - e^{- \frac{\tmp{u}}{\param{m}} \param{t}}\right) - \param{v},$$ without the "
                "cancellation that makes the published function exactly 0 at many x-values next to the "
                "root."
            ),
            r"$\operatorname{expm1}(z)$ is $e^z - 1$, computed without cancellation for a small $z$.",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, g: float, m: float, v: float, t: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(g*m/y)*(-expm1(-(y/m)*t)) - v``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return (g * m / x) * -math.expm1(-(x / m) * t) - v

    def interval_bounds(self, g: float, m: float, v: float, t: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problem."""
        return (
            ParamTable(
                names=("g", "m", "v", "t"),
                rows=((9.81, 82.0, 36.0, 4.0),),
                summary="The published parameter values on $[3, 5]$.",
            ),
        )

    test_cases = (
        FormulaTestCase.interval_bounds(params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0}, expected=(3.0, 5.0)),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0}, x=3.6, c=0.25, expected=0.417138544494483
        ),
    )
