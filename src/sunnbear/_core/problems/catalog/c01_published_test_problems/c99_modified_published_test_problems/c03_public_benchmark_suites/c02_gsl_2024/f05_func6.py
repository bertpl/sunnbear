"""This module holds formula f1.99.3.2.5, the modified version of the published formula f1.3.2.5.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.2.5 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedGsl2024Func6(Formula):
    """This formula is the modified version of formula f1.3.2.5, from GSL (2024).

    The survey writes the source's function as ``(x - 1)^7``; the published interval is ``[0.9995, 1.0002]``.

    Starting point 0.9, run by `steffenson` only; derivative given

    The formula evaluates ``x**7``, the published function at ``x + 1``, on the published interval shifted by -1,
    ``[-0.0005, 0.0002]``, which lies around 0; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded
    width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because its interval is
    narrow around the root at 1: the ratio of the interval's largest bound to its width, about 1429, is above the
    conditions' limit of 100.

    The published function evaluated at ``x + 1`` does not satisfy the conditions either, because they require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0
    of f. Adding 1 to x rounds x to the spacing of the floats near 1, about 2.2e-16, so that f is exactly 0 where
    ``abs(x)`` is below about 1.1e-16; ``x**7`` adds nothing to x, so it does not round x.
    """

    number = (1, 99, 3, 2, 5)
    name = "func6"
    param_names = ()
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="func6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c + 1``, as ``(x - c_scale*c)**7``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.0007 * c
        return x**7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.0005, 0.0002)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-0.0005, 0.0002)),
        FormulaTestCase.value(params={}, x=-0.00029, c=0.25, expected=-4.700788051621643e-24, atol=0.0),
    )
