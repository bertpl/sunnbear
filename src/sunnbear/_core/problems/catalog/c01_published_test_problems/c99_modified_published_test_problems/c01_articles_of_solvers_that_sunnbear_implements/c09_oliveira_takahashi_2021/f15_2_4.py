"""This module holds formula f1.99.1.9.15, the modified version of the published formula f1.1.9.15.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.9.15 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class ModifiedOliveiraTakahashi202124(Formula):
    """This formula is the modified version of formula f1.1.9.15, from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``sign(3*x + 1)*(1 - sqrt(1 - (3*x + 1)^2/9^2))``; the published interval
    is ``[-1, 1]``.

    The formula computes the published function in the equivalent form
    ``sign(3*x + 1) * ((3*x + 1)**2/9**2) / (1 + sqrt(1 - (3*x + 1)**2/9**2))``, on the published interval, and ``c``
    shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``sqrt(1 - (3*x + 1)**2/9**2)`` rounds to 1, and its subtraction from 1 cancels, so that f is exactly
    0 at many x-values within about 2e-8 of the root; the equivalent form has no subtraction that cancels.
    """

    number = (1, 99, 1, 9, 15)
    name = "2.4"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method "
            "average performance preserving minmax optimality. ACM Transactions on Mathematical "
            "Software 47(1), Article 5. https://doi.org/10.1145/3423597. The article itself is dated "
            "December 2020."
        ),
        location="2.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, in an equivalent form without cancellation.

        The form is ``sign(3*y + 1) * ((3*y + 1)**2/9**2) / (1 + sqrt(1 - (3*y + 1)**2/9**2))``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return sign(3 * x + 1) * ((3 * x + 1) ** 2 / 9**2) / (1 + math.sqrt(1 - (3 * x + 1) ** 2 / 9**2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.018001533782093432),
    )
