"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key
``(PT2.3), (PT2.4); Ex. 5.1, 5.3–5.5; Fig. 5.1, 5.6, 5.7, 5.13; Prob. 5.14, 5.21, 5.23, 5.26, 7.20, 7.21`` in the survey
of published test problems. The module generator, `scripts/literature_test_problems/formula_modules.py`, does not write
a formula with the parameter ``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale2015Pt23(Formula):
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

    Only the test problem on ``[3, 5]`` has a version with ``modified = 1``, which computes the published function in
    the equivalent form ``(g*m/x)*(-expm1(-(x/m)*t)) - v``, on that interval; ``c`` shifts x as category 1 states.

    The published test problem on ``[3, 5]`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 3e-14 of
    the root. ``-expm1(-(x/m)*t)`` computes ``1 - exp(-(x/m)*t)`` without the subtraction; the subtraction of ``v``
    stays, because it is the function's definition: the velocity after ``t`` seconds minus ``v``.

    The test problem with ``modified = 1`` does not satisfy the conditions either, because the subtraction of ``v``
    leaves f exactly 0 at x-values within about 8 floats of the root, on which bisection can land.
    """

    number = (1, 4, 6, 1)
    name = "(PT2.3)"
    param_names = ("g", "m", "v", "t", "a", "b", "c_scale", "modified")
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
    def parametrized_fun(
        x: float, c: float, g: float, m: float, v: float, t: float, a: float, b: float, c_scale: float, modified: float
    ) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``(g*m/y)*(-expm1(-(y/m)*t)) - v``, with ``y = x - c_scale*c``. Category
        1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            return (g * m / x) * -math.expm1(-(x / m) * t) - v
        else:
            return (g * m / x) * (1 - math.exp(-(x / m) * t)) - v

    def interval_bounds(
        self, g: float, m: float, v: float, t: float, a: float, b: float, c_scale: float, modified: float
    ) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(
                names=("g", "m", "v", "t", "a", "b", "c_scale", "modified"),
                rows=(
                    (9.81, 68.1, 40.0, 10.0, 12.0, 16.0, 4.0, 0.0),
                    (9.81, 68.1, 40.0, 10.0, 4.0, 20.0, 16.0, 0.0),
                    (9.81, 82.0, 36.0, 4.0, 3.0, 5.0, 2.0, 0.0),
                ),
            ),
            ParamTable(
                names=("g", "m", "v", "t", "a", "b", "c_scale", "modified"),
                rows=((9.81, 82.0, 36.0, 4.0, 3.0, 5.0, 2.0, 1.0),),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0, "modified": 0.0},
            x=13.2,
            c=0.0,
            expected=3.325541753212046,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0, "modified": 0.0},
            x=13.2,
            c=0.25,
            expected=5.630059449656643,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 4.0, "b": 20.0, "c_scale": 16.0, "modified": 0.0},
            x=8.8,
            c=0.0,
            expected=15.064844887009704,
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 0.0},
            x=3.6,
            c=0.0,
            expected=-0.012330135450636158,
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 12.0, "b": 16.0, "c_scale": 4.0, "modified": 0.0},
            expected=(12.0, 16.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 68.1, "v": 40.0, "t": 10.0, "a": 4.0, "b": 20.0, "c_scale": 16.0, "modified": 0.0},
            expected=(4.0, 20.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 0.0},
            expected=(3.0, 5.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 1.0},
            expected=(3.0, 5.0),
        ),
        FormulaTestCase.value(
            params={"g": 9.81, "m": 82.0, "v": 36.0, "t": 4.0, "a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 1.0},
            x=3.6,
            c=0.25,
            expected=0.417138544494483,
        ),
    )
