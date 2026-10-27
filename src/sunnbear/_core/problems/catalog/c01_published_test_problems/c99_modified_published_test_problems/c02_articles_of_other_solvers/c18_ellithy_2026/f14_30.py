"""This module holds formula f1.99.2.18.14, the modified version of the published formula f1.2.18.14.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.18.14 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEllithy202630(Formula):
    """This formula is the modified version of formula f1.2.18.14, from Ellithy (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - 30: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the published interval is ``[0,
      1.5]``
    - 31: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the published interval is ``[19,
      21]``

    The function is Wilkinson's polynomial, which the author's file writes out as the product of all 20 factors ``(x -
    1)`` to ``(x - 20)``.

    The formula holds only the test problem of row 31. The formula changes the published interval ``[19, 21]`` to
    ``[19.02, 21]``: its lower bound moves right of the root at 19 by 1% of the published interval's width, rounded half
    up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[19, 21]`` does not satisfy the benchmark suite inclusion conditions, because
    ``f(a)`` is 0 at the root ``a = 19``.
    """

    number = (1, 99, 2, 18, 14)
    name = "30"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="30, 31",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.98 * c
        # the loop multiplies the 20 factors (x - 1) to (x - 20) from the left, in the order of the author's file
        product = x - 1
        for i in range(2, 21):
            product *= x - i
        return product

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (19.02, 21.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=19.6, c=0.25, expected=-861217411598204.5),
        FormulaTestCase.interval_bounds(params={}, expected=(19.02, 21.0)),
    )
