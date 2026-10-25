"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``T4.7`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so the module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write it.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a published
test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class Gao2026T47(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-1/x^2)`` if ``x != 0``; the formula's
    intervals are ``[-1, 4]``; ``[-2, 5]``; ``[-1, 10]``; ``[-5, 50]``; ``[-10, 100]``.

    With ``modified = 1``, the formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the published function, on the published
    intervals; ``c`` shifts x as category 1 states, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is
    ``2**-918``.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range, so that no form of it avoids the zeros. With the term, f is exactly 0 only within about 5e-48
    of the root, where the term underflows too; beyond about 0.04 from the root, the term changes f by less than its
    rounding.

    With ``modified = 1``, the modification changes what the test problem tests: in float64, the published function is
    exactly 0 within about 0.04 of the root, so that a solver may stop at any x-value there, while with the term a
    solver must locate the root, near which f is the linear term.
    """

    number = (1, 1, 14, 5)
    name = "T4.7"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied "
            "Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        location="T4.7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, add ``TINY_LINEAR_TERM_SLOPE*y``, with ``y = x - c_scale*c``. Category 1 states the rule
        for ``c_scale``.
        """
        x = x - c_scale * c
        # below 1e-100, float64 rounds x*exp(-1/x^2) to 0, and x**2 underflows to 0
        if abs(x) < 1e-100:
            published_value = 0.0
        else:
            published_value = x * math.exp(-1 / x**2)
        if modified == 1:
            return published_value + TINY_LINEAR_TERM_SLOPE * x
        else:
            return published_value

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (-1.0, 4.0, 5.0, 0.0),
                    (-2.0, 5.0, 7.0, 0.0),
                    (-1.0, 10.0, 11.0, 0.0),
                    (-5.0, 50.0, 55.0, 0.0),
                    (-10.0, 100.0, 110.0, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (-1.0, 4.0, 5.0, 1.0),
                    (-2.0, 5.0, 7.0, 1.0),
                    (-1.0, 10.0, 11.0, 1.0),
                    (-5.0, 50.0, 55.0, 1.0),
                    (-10.0, 100.0, 110.0, 1.0),
                ),
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 0.0}, x=0.5, c=0.0, expected=0.00915781944436709
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 0.0}, x=0.5, c=0.25, expected=-0.12675998655454956
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 0.0}, x=0.0, c=0.0, expected=0.0
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 0.0}, x=1e-200, c=0.0, expected=0.0
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0, "modified": 0.0},
            x=0.1,
            c=0.0,
            expected=3.7200759760208773e-45,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0, "modified": 0.0}, x=2.3, c=0.0, expected=1.9038405842623145
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0, "modified": 0.0}, x=11.5, c=0.0, expected=11.413371409313232
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0, "modified": 0.0},
            x=23.0,
            c=0.0,
            expected=22.956562808012574,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 0.0}, expected=(-1.0, 4.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0, "modified": 0.0}, expected=(-2.0, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0, "modified": 0.0}, expected=(-1.0, 10.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0, "modified": 0.0}, expected=(-5.0, 50.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0, "modified": 0.0}, expected=(-10.0, 100.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 1.0}, expected=(-1.0, 4.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 1.0}, x=0.5, c=0.25, expected=-0.12675998655454956
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0, "modified": 1.0},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0, "modified": 1.0}, expected=(-2.0, 5.0)
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0, "modified": 1.0},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0, "modified": 1.0}, expected=(-1.0, 10.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0, "modified": 1.0},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0, "modified": 1.0}, expected=(-5.0, 50.0)
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0, "modified": 1.0},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0, "modified": 1.0}, expected=(-10.0, 100.0)
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0, "modified": 1.0},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
    )
