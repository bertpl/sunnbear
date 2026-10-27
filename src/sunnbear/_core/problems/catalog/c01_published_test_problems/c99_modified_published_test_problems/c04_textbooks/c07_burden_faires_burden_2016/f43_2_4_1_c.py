"""This module holds formula f1.99.4.7.43, the modified version of the published formula f1.4.7.43.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.43 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016241C(Formula):
    """This formula is the modified version of formula f1.4.7.43, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 3*x^2*(2^-x) + 3*x*(4^-x) - 8^-x``; the published interval is
    ``[0, 1]``.

    As 2.4-1(a). It equals `(x - 2^-x)^3`, the cube of 2.1-5(a)'s function.

    The formula computes the published function in the equivalent form ``(x - 2**-x)**3``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the 4 terms of the published form cancel, so that f is exactly 0 at many x-values within about 5e-6
    of the root; in ``(x - 2**-x)**3``, only the rounding of ``x - 2**-x`` can change the sign of f, and ``x - 2**-x``
    has a simple root, so that the sign of f can be wrong only at x-values at most about 1 float64 value away from the
    root.
    """

    number = (1, 99, 4, 7, 43)
    name = "2.4-1(c)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-1(c)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(y - 2**-y)**3``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        return (x - 2**-x) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.7684150363472455),
    )
