"""This module holds formula f1.99.4.5.8, the modified version of the published formula f1.4.5.8.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.5.8 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEpperson2013313H(Formula):
    """This formula is the modified version of formula f1.4.5.8, from Epperson (2013).

    The survey writes the source's function as ``x^2 - sin(x)``; the published interval is ``[0, pi]``.

    Bisection to `1E-6`; Newton from `x0 = 1/2`.

    The formula changes the published interval ``[0, pi]`` to ``[0.03, pi]``: the lower bound moves right of the root at
    0 by 1% of the published interval's width, rounded half up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` is 0 at the
    root ``a = 0``.
    """

    number = (1, 99, 4, 5, 8)
    name = "3.1-3(h)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.1-3(h); 3.2-5(e); 3.3-3(g)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.11 * c
        return x**2 - math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.03, 3.141592653589793)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.963478, c=0.25, expected=-0.15031994057295994),
        FormulaTestCase.interval_bounds(params={}, expected=(0.03, 3.141592653589793)),
    )
