"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.8`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Sabharwal2019T28(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x*exp(x) - 7``; the formula's interval is ``[-1, 1]``.

    Printed `xe^x - 7`. No sign change and no root on `[-1, 1]`: the only real root is about `1.5243`.

    With ``modified = 1``, the interval ``[-1, 1]`` becomes ``[-1, 2]``: its upper bound moves right of the function's
    root, near 1.52, so that the interval holds that root. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the root lies outside
    the published interval, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 2, 13, 9)
    name = "T2.8"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x * math.exp(x) - 7

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.0, 1.0, 2.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.0, 2.0, 3.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, x=-0.4, c=0.0, expected=-7.268128018414256
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, x=-0.4, c=0.25, expected=-7.365912693766539
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, expected=(-1.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 2.0, "c_scale": 3.0, "modified": 1.0}, x=-0.1, c=0.25, expected=-7.3633026921564175
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 2.0, "c_scale": 3.0, "modified": 1.0}, expected=(-1.0, 2.0)
        ),
    )
