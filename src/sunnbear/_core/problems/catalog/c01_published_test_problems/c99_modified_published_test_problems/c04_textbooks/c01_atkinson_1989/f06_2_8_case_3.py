"""This module holds formula f1.99.4.1.6, the modified version of the published formula f1.4.1.6.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.1.6 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedAtkinson198928Case3(Formula):
    """This formula is the modified version of formula f1.4.1.6, from Atkinson (1989).

    The survey writes the source's function as ``-1 + x*(3 + x*(-3 + x))``; the published interval is ``[0, 3]``.

    Triple root 1: Brent's algorithm takes 50 iterations to reach 1.000001, where bisection would take 19.

    The formula computes the published function in the equivalent form ``(x - 1)**3``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 7e-6 of
    the root; ``(x - 1)**3`` has no terms that cancel.
    """

    number = (1, 99, 4, 1, 6)
    name = "§2.8 case (3)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (3); P34(iii)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 1)**3``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.0 * c
        return (x - 1) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-0.6141249999999999),
    )
