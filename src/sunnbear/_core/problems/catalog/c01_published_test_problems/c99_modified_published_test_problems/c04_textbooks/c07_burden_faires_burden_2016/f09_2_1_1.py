"""This module holds formula f1.99.4.7.9, the modified version of the published formula f1.4.7.9.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.9 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016211(Formula):
    """This formula is the modified version of formula f1.4.7.9, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sqrt(x) - cos(x)``; the published interval is ``[0, 1]``.

    Bisection to `p3`.

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because a shift along x by
    any ``c > 0`` evaluates ``sqrt(x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 99, 4, 7, 9)
    name = "2.1-1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return math.sqrt(x) - math.cos(x) + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.1576139316204399),
        FormulaTestCase.value(params={}, x=0.0, c=0.25, expected=-0.75),
    )
