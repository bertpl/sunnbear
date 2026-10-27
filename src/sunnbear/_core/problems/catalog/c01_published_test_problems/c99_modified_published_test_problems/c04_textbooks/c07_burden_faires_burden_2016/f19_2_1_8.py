"""This module holds formula f1.99.4.7.19, the modified version of the published formula f1.4.7.19.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.19 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016218(Formula):
    """This formula is the modified version of formula f1.4.7.19, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = tan(x)``; the published interval is `[4, 5]` (2.2-16).

    The first positive solution by bisection to `1E-5` (2.1-8); the solution in `[4, 5]` by fixed-point iteration to
    `1E-4` (2.2-16).

    The formula changes the published interval ``[4, 5]`` to ``[4, 4.6]``: the upper bound moves left of the pole of
    ``tan(x)`` at ``3*pi/2``, near 4.71, so that the interval holds its root and no pole; ``c`` shifts x by the rule of
    category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the pole inside the
    published interval is a second sign change, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 7, 19)
    name = "2.1-8"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-8; 2.2-16",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.6 * c
        return (x) - (math.tan(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 4.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.18, c=0.25, expected=2.7994128881553113),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 4.6)),
    )
