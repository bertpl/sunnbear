"""This module holds formula f1.99.2.18.5, the modified version of the published formula f1.2.18.5.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.18.5 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedEllithy202620(Formula):
    """This formula is the modified version of formula f1.2.18.5, from Ellithy (2026).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``exp(x^2) - exp(k*x)``:

    - 20, with ``k = 2^(1/2)``: ``exp(x^2) - exp(sqrt(2)*x)``; the published interval is ``[0.5, 1.5]``
    - 39, with ``k = 1.2``: ``exp(x^2) - exp(1.2*x)``; the published interval is ``[0, 2]``

    The formula holds only the test problem with ``k = 1.2``. It changes the published interval ``[0, 2]`` to
    ``[0.02, 2]``: its lower bound moves right of the root at 0 by 1% of the published interval's width, rounded half up
    to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[0, 2]`` does not satisfy the benchmark suite inclusion conditions, because
    ``f(a)`` is 0 at the root ``a = 0``.
    """

    number = (1, 99, 2, 18, 5)
    name = "20"
    param_names = ("k",)
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="20, 39",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.98 * c
        return math.exp(x**2) - math.exp(k * x)

    def interval_bounds(self, k: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.02, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter value of the modified test problem."""
        return (ParamTable(names=("k",), rows=((1.2,),)),)

    test_cases = (
        FormulaTestCase.value(params={"k": 1.2}, x=0.614, c=0.25, expected=-0.1392373368444251),
        FormulaTestCase.interval_bounds(params={"k": 1.2}, expected=(0.02, 2.0)),
    )
