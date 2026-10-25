"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.10`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# ROOT is the float64 nearest to the published polynomial's root near 5.61.
ROOT = 5.609788960859374
# TAYLOR_COEFFICIENTS holds the published polynomial's Taylor coefficients at ROOT, of t**0 to t**3 with t = x - ROOT;
# the coefficient of t**4 is 1. They are computed with mpmath from the published coefficients and rounded to float64.
TAYLOR_COEFFICIENTS = (4.692574564789708e-16, 8.195425149706974, 19.183458051653208, 14.439155843437497)


class ChapraCanale2015Prob510(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^4 - 8*x^3 - 35*x^2 + 450*x - 1001``; the formula's interval is
    ``[4.5, 6]``.

    Positive real root 5.60979, as the book states; 5 false-position iterations, a plot to explain the result, then
    false position to `es = 1.0%`.

    With ``modified = 1``, the formula computes the published polynomial in its re-expansion around ``ROOT``, the
    float64 nearest to its root, on the published interval; ``c`` shifts x as category 1 states. The re-expansion is
    ``c0 + t*(c1 + t*(c2 + t*(c3 + t)))``, with ``t = x - ROOT`` and ``c0`` to ``c3`` from `TAYLOR_COEFFICIENTS`.

    A factored form ``(x - r)*q(x)`` would not cancel near the root, but the polynomial has no such form with exact
    float64 coefficients, so the formula re-expands the polynomial. Near the root, ``c0`` and ``c1*t`` are small, and
    the other terms are smaller still, so f is not a difference of large, nearly equal terms. Rounding the coefficients
    to float64 moves the root by a negligible fraction of the float64 spacing there.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 6e-14 of
    the root.
    """

    number = (1, 4, 6, 18)
    name = "Prob. 5.10"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.10",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate the published function in its re-expansion around ``ROOT``, with
        ``t = x - c_scale*c - ROOT``. Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.5 * c
        if modified == 1:
            c0, c1, c2, c3 = TAYLOR_COEFFICIENTS
            t = x - ROOT
            return c0 + t * (c1 + t * (c2 + t * (c3 + t)))
        else:
            return x**4 - 8 * x**3 - 35 * x**2 + 450 * x - 1001

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.5, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=4.95, c=0.0, expected=-1.0139937499999998),
        FormulaTestCase.value(params={"modified": 0.0}, x=4.95, c=0.25, expected=-2.791687109374998),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(4.5, 6.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(4.5, 6.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=4.95, c=0.25, expected=-2.791687109374998),
    )
