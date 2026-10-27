"""This module holds formula f1.99.4.7.47, the modified version of the published formula f1.4.7.47.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.47 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016242C(Formula):
    """This formula is the modified version of formula f1.4.7.47, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sin(x)^3 + 3*exp(-2*x)*sin(x) - 3*exp(-x)*sin(x)^2 - exp(-3*x)``; the
    published interval is ``[3, 4]``.

    As 2.4-2(a). The book prints `sin 3x` and `sin 2x`, misprints for `sin(x)^3` and `sin(x)^2`: with them the 4 terms
    are the expansion of `(sin(x) - exp(-x))^3`, the cube of 2.3-6(f)'s function on the same `[3, 4]`, with a triple
    root at 3.096364. Every other part of 2.4-1 and 2.4-2 has a multiple root too (2.4-2(b) once its misprint is
    corrected). As printed, the function has a simple root at 3.141568.

    The formula computes the published function in the equivalent form ``(sin(x) - exp(-x))**3``, on the published
    interval; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the 4 terms of the published form cancel, so that f is exactly 0 at many x-values within about 1e-6
    of the root; in ``(sin(x) - exp(-x))**3``, only the rounding of ``sin(x) - exp(-x)`` can change the sign of f, and
    ``sin(x) - exp(-x)`` has a simple root, so that the sign of f can be wrong only at x-values at most about 1 float64
    value away from the root.
    """

    number = (1, 99, 4, 7, 47)
    name = "2.4-2(c)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-2(c)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(sin(y) - exp(-y))**3``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        return (math.sin(x) - math.exp(-x)) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 4.0)),
        FormulaTestCase.value(params={}, x=3.3, c=0.25, expected=8.579948567035882e-05),
    )
