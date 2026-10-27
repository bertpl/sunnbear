"""This module holds formula f1.99.4.5.23, the modified version of the published formula f1.4.5.23.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.5.23 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEpperson201331125(Formula):
    """This formula is the modified version of formula f1.4.5.23, from Epperson (2013).

    The survey writes the source's function as ``(x - 1)^5``; the published interval is ``[0.998, 1.002]``.

    Evaluated at 400 points in 3 forms: `(x - 1)^5`, `x^5 - 5*x^4 + 10*x^3 - 10*x^2 + 5*x - 1` and `-1 + x*(5 + x*(-10 +
    x*(10 + x*(-5 + x))))`.

    The formula evaluates ``x**5``, the published function at ``x + 1``, on the published interval shifted by -1,
    ``[-0.002, 0.002]``, which lies around 0; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded
    width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because its interval is
    narrow around the root at 1: the ratio of the interval's largest bound to its width, about 250, is above the
    conditions' limit of 100.

    The published function evaluated at ``x + 1`` does not satisfy the conditions either, because they require bisection
    to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of f. Adding
    1 to x rounds x to the spacing of the floats near 1, about 2.2e-16, so that f is exactly 0 where ``abs(x)`` is below
    about 1.1e-16; ``x**5`` adds nothing to x, so it does not round x.
    """

    number = (1, 99, 4, 5, 23)
    name = "3.11-25"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.11-25",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c + 1``, as ``(x - c_scale*c)**5``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.004 * c
        return x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.002, 0.002)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-0.002, 0.002)),
        FormulaTestCase.value(params={}, x=-0.0008, c=0.25, expected=-1.889568e-14, atol=0.0),
    )
