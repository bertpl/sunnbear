"""This module holds formula f1.99.4.1.8, the modified version of the published formula f1.4.1.8.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.1.8 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedAtkinson1989P38A(Formula):
    """This formula is the modified version of formula f1.4.1.8, from Atkinson (1989).

    The survey writes the source's function as ``x^4 - 5.7*x^3 - 0.47*x^2 + 29.865*x - 26.1602``; the published interval
    is ``[-3, 5]``.

    Evaluated in single and double precision, in steps of `h = 0.1`, to measure the noise; P41 finds the roots with a
    polynomial package.

    The formula changes the published interval ``[-3, 5]`` to ``[-3, 4]``: its upper bound moves left of the last root,
    near 4.7, so that the interval holds 3 of the 4 roots. ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 4 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 1, 8)
    name = "P38(a)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="P38(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 7.0 * c
        return x**4 - 5.7 * x**3 - 0.47 * x**2 + 29.865 * x - 26.1602

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.9, c=0.25, expected=46.787343749999984),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 4.0)),
    )
