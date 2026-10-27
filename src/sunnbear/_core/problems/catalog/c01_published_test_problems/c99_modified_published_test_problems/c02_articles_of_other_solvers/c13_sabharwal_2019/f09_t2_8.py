"""This module holds formula f1.99.2.13.9, the modified version of the published formula f1.2.13.9.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.13.9 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedSabharwal2019T28(Formula):
    """This formula is the modified version of formula f1.2.13.9, from Sabharwal (2019).

    The survey writes the source's function as ``x*exp(x) - 7``; the published interval is ``[-1, 1]``.

    Printed `xe^x - 7`. No sign change and no root on `[-1, 1]`: the only real root is about `1.5243`.

    The formula changes the published interval ``[-1, 1]`` to ``[-1, 2]``: its upper bound moves right of the function's
    root, near 1.52, so that the interval holds that root. ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the root lies outside
    the published interval, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 2, 13, 9)
    name = "T2.8"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.25, expected=-7.3633026921564175),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
