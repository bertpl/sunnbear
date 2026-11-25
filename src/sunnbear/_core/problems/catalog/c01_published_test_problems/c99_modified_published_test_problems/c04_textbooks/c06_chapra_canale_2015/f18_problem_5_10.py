"""This module holds formula f1.99.4.6.18, the modified version of the published formula f1.4.6.18.

A change of formula f1.4.6.18 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)

# ROOT is the float64 nearest to the published polynomial's root near 5.61.
ROOT = 5.609788960859374
# TAYLOR_COEFFICIENTS holds the coefficients of t**0 to t**3 in the published polynomial's Taylor expansion at ROOT,
# with t = x - ROOT; the coefficient of t**4 is 1. They are computed with mpmath from the published coefficients and
# rounded to float64.
TAYLOR_COEFFICIENTS = (4.692574564789708e-16, 8.195425149706974, 19.183458051653208, 14.439155843437497)


class ModifiedChapraCanale2015Problem510(Formula):
    """This formula is the modified version of formula f1.4.6.18, from Chapra, Canale (2015).

    The survey writes the source's function as ``x^4 - 8*x^3 - 35*x^2 + 450*x - 1001``; the published interval is
    ``[4.5, 6]``.

    Positive real root 5.60979, as the book states; 5 false-position iterations, a plot to explain the result, then
    false position to `es = 1.0%`.

    The formula computes the published polynomial in its re-expansion around ``ROOT``, the float64 nearest to the
    polynomial's root, on the published interval.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval. The
    re-expansion is ``c0 + t*(c1 + t*(c2 + t*(c3 + t)))``, with ``t = x - ROOT`` and ``c0`` to ``c3`` from
    `TAYLOR_COEFFICIENTS`.

    The formula re-expands the polynomial because the polynomial has no factored form ``(x - r)*q(x)`` with exact
    float64 coefficients, with ``r`` the root and ``q`` a cubic polynomial; such a form would have no terms that cancel
    near the root.

    Near the root, ``c0`` and ``c1*t`` are small, and the other terms are smaller still, so f is not a difference of
    large, nearly equal terms. Rounding the coefficients to float64 moves the root by a negligible fraction of the
    float64 spacing at the root.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 6e-14 of
    the root.
    """

    number = (1, 99, 4, 6, 18)
    name = "Problem 5.10"
    params = ()
    location_in_publication = "Prob. 5.10"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \c"),
            (r"\tmp{t}", r"\tmp{u} - 5.609788960859374"),
        ),
        expression=(
            r"4.692574564789708 \cdot 10^{-16} + \tmp{t} \left(8.195425149706974 + \tmp{t} "
            r"\left(19.183458051653208 + \tmp{t} \left(14.439155843437497 + "
            r"\tmp{t}\right)\right)\right)"
        ),
        interval="[4.5, 6]",
        summary=(
            "A quartic with 1 simple root on the interval and, left of that root, a local maximum of $-1$ and a "
            "local minimum only 0.12 lower."
        ),
        notes=(
            (
                r"The expression is the Taylor expansion of the published polynomial, $$\tmp{u}^{4} - 8 "
                r"\tmp{u}^{3} - 35 \tmp{u}^{2} + 450 \tmp{u} - 1001,$$ at the float64 value nearest to its "
                "root, with its coefficients rounded to float64. Unlike the published form, it has no "
                "terms that cancel next to the root, where the published polynomial is exactly 0 at many "
                "x-values."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function in its re-expansion around ``ROOT``, with ``t = x - c_scale*c - ROOT``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        c0, c1, c2, c3 = TAYLOR_COEFFICIENTS
        t = x - ROOT
        return c0 + t * (c1 + t * (c2 + t * (c3 + t)))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.5, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(4.5, 6.0)),
        FormulaTestCase.value(params={}, x=4.95, c=0.375, expected=-2.791687109374998),
    )
