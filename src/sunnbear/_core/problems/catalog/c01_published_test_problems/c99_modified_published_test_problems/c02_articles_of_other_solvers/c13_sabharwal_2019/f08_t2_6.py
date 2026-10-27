"""This module holds formula f1.99.2.13.8, the modified version of the published formula f1.2.13.8.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.13.8 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedSabharwal2019T26(Formula):
    """This formula is the modified version of formula f1.2.13.8, from Sabharwal (2019).

    The survey writes the source's function as ``x^2 + 5*x + 2``; the published interval is ``[-6, 0]``.

    No sign change on `[-6, 0]`, which holds both roots, `(-5 - sqrt(17))/2` and `(-5 + sqrt(17))/2`.

    The formula changes the published interval ``[-6, 0]`` to ``[-6, -0.9]``: its upper bound moves left of the second
    root, near -0.44, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 2, 13, 8)
    name = "T2.6"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.1 * c
        return x**2 + 5 * x + 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-6.0, -0.9)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.47, c=0.25, expected=6.280024999999995),
        FormulaTestCase.interval_bounds(params={}, expected=(-6.0, -0.9)),
    )
