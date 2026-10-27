"""This module holds formula f1.99.4.6.1, the modified version of the published formula f1.4.6.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.6.1 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChapraCanale2015Pt23(Formula):
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

    The formula holds only the test problem on ``[3, 5]``. It computes the published function in the equivalent form
    ``(g*m/x)*(-expm1(-(x/m)*t)) - v``, on that interval; ``c`` shifts x by the rule of category 1, with ``c_scale`` the
    rounded width of the published interval.

    The published test problem on ``[3, 5]`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 3e-14 of
    the root.

    ``-expm1(-(x/m)*t)`` computes ``1 - exp(-(x/m)*t)`` without the subtraction; the subtraction of ``v`` stays, because
    it is the function's definition: the velocity after ``t`` seconds minus ``v``.

    The subtraction of ``v`` still leaves f exactly 0 at x-values at most about 8 float64 values away from the root, so
    that bisection can still stop early for some values of ``c``. The formula modifies the function no further, because
    no equivalent form removes the subtraction of ``v``.
    """

    number = (1, 99, 4, 6, 1)
    name = "(PT2.3)"
    param_names = ("g", "m", "v", "t")
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location=(
            "(PT2.3), (PT2.4); Ex. 5.1, 5.3–5.5; Fig. 5.1, 5.6, 5.7, 5.13; Prob. 5.14, 5.21, 5.23, 5.26, 7.20, 7.21"
        ),
    )

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
        return (ParamTable(names=("g", "m", "v", "t"), rows=((9.81, 82.0, 36.0, 4.0),)),)

    test_cases = (
        FormulaTestCase.interval_bounds(params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0}, expected=(3.0, 5.0)),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0}, x=3.6, c=0.25, expected=0.417138544494483
        ),
    )
