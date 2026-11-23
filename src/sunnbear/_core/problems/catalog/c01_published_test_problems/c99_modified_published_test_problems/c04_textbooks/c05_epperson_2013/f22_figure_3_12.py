"""This module holds formula f1.99.4.5.22, the modified version of the published formula f1.4.5.22.

A change of formula f1.4.5.22 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEpperson2013Figure312(Formula):
    """This formula is the modified version of formula f1.4.5.22, from Epperson (2013).

    The survey writes the source's function as ``x^5 - (5/2)*x^4 + (5/2)*x^3 - (5/4)*x^2 + (5/16)*x - 1/32``; the
    published interval is ``[0.45, 0.55]``.

    Printed also as `(x - 1/2)^5`. Evaluated in floating point at 8000 points of the interval, its values form a band
    around 0.

    The formula computes the published function in the equivalent form ``(x - 0.5)**5``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 7e-4 of
    the root; ``(x - 0.5)**5`` has no terms that cancel.

    The modification changes what the test problem tests: the source evaluates f at 8000 points of the interval to show
    that near the multiple root the values of f form a band around 0, inside which a root-finding method's iterations
    stop early (Figure 3.12).

    ``(x - 0.5)**5`` has no such band.
    """

    number = (1, 99, 4, 5, 22)
    name = "Figure 3.12"
    params = ()
    location_in_publication = "§3.11.4, Fig. 3.12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.1 \c"),),
        expression=r"\left(\tmp{u} - 0.5\right)^{5}",
        interval="[0.45, 0.55]",
        summary=(
            r"A 5th power whose magnitude stays below $4 \cdot 10^{-7}$ on the whole interval and at most about "
            r"$10^{-10}$ on its middle 20%."
        ),
        notes=(
            (
                r"The expression equals the published function, $$\tmp{u}^{5} - \frac{5 \tmp{u}^{4}}{2} + "
                r"\frac{5 \tmp{u}^{3}}{2} - \frac{5 \tmp{u}^{2}}{4} + \frac{5 \tmp{u}}{16} - "
                r"\frac{1}{32},$$ without the cancellation that makes the published function exactly 0 at "
                "many x-values next to the root."
            ),
            (
                "This changes what the test problem tests: the source evaluates the published function at "
                "8000 points to show that next to the multiple root its values form a band around 0, "
                "inside which a method's iterations stop early, and the expression has no such band."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 0.5)**5``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.1 * c
        return (x - 0.5) ** 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.45, 0.55)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.45, 0.55)),
        FormulaTestCase.value(params={}, x=0.48, c=0.25, expected=-1.8452812500000082e-07),
    )
