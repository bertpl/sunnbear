"""This module holds formula f1.99.4.7.48, the modified version of the published formula f1.4.7.48.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.48 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016242D(Formula):
    """This formula is the modified version of formula f1.4.7.48, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(3*x) - 27*x^6 + 27*x^4*exp(x) - 9*x^2*exp(2*x)``; the published
    interval is ``[3, 5]``.

    As 2.4-2(a). It equals `(exp(x) - 3*x^2)^3`, the cube of 2.3-6(e)'s function.

    The formula computes the published function in the equivalent form ``(exp(x) - 3*x**2)**3``, on the published
    interval; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the 4 terms of the published form cancel, so that f is exactly 0 at many x-values within about 4e-5
    of the root; in ``(exp(x) - 3*x**2)**3``, only the rounding of ``exp(x) - 3*x**2`` can change the sign of f, and
    ``exp(x) - 3*x**2`` has a simple root, so that the sign of f can be wrong only at x-values at most about 1 float64
    value away from the root.
    """

    number = (1, 99, 4, 7, 48)
    name = "2.4-2(d)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-2(d)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(exp(y) - 3*y**2)**3``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return (math.exp(x) - 3 * x**2) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 5.0)),
        FormulaTestCase.value(params={}, x=3.6, c=0.25, expected=-291.7044964422511),
    )
