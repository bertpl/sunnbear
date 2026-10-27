"""This module holds formula f1.99.1.12.1, the modified version of the published formula f1.1.12.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.12.1 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedGorgeyEtAl2025Equation1(Formula):
    """This formula is the modified version of formula f1.1.12.1, from Gorgey et al. (2025).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the published intervals are `[-2.5, 3]`;
    `[2, 3.5]` (Figure 1's caption and the text below Table 2).

    Roots `-2`, `-1` and `3`; the text names `3` as the root found.

    The formula holds only the test problem on ``[-2.5, 3]``. The interval ``[-2.5, 3]`` becomes ``[-2.5, 3.06]``: its
    upper bound moves right of the triple root at 3 by 1% of the published interval's width, rounded half up to 1
    significant digit, so that ``b`` is not a root and the interval holds all 3 roots, -2, -1 and 3; ``c`` shifts x by
    the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[-2.5, 3]`` does not satisfy the benchmark suite inclusion conditions, because
    ``f(b)`` is 0 at the triple root ``b = 3``.
    """

    number = (1, 99, 1, 12, 1)
    name = "Equation 1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.56 * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.5, 3.06)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.832, c=0.25, expected=-38.63089614110562),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.5, 3.06)),
    )
