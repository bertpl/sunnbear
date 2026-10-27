"""This module holds formula f1.99.2.18.6, the modified version of the published formula f1.2.18.6.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.18.6 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEllithy202621(Formula):
    """This formula is the modified version of formula f1.2.18.6, from Ellithy (2026).

    The survey writes the source's function as ``(x^2 - 4)*(x + 1.5)*(x - 0.5)``; the published interval is ``[0, 2]``.

    The formula changes the published interval ``[0, 2]`` to ``[0, 1.98]``: its upper bound moves left of the root at 2
    by 1% of the published interval's width, rounded half up to 1 significant digit. ``c`` shifts x by the rule of
    category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(b)`` is 0 at the
    root ``b = 2``.
    """

    number = (1, 99, 2, 18, 6)
    name = "21"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="21",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.98 * c
        return (x**2 - 4) * (x + 1.5) * (x - 0.5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.98)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.594, c=0.25, expected=2.558511608601),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.98)),
    )
