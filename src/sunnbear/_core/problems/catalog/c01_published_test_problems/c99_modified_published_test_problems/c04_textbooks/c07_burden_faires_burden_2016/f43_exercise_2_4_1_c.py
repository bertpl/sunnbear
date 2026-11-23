"""This module holds formula f1.99.4.7.43, the modified version of the published formula f1.4.7.43.

A change of formula f1.4.7.43 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurdenFairesBurden2016Exercise241C(Formula):
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
    name = "Exercise 2.4-1(c)"
    params = ()
    location_in_publication = "Exercise 2.4-1(c)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u} - 2^{- \tmp{u}}\right)^{3}",
        interval="[0, 1]",
        summary=(
            "An increasing cube that stays below $10^{-3}$ in magnitude on a band 0.14 wide around the triple root."
        ),
        notes=(
            (
                r"The expression equals the published function, $$\tmp{u}^{3} - 3 \tmp{u}^{2} \cdot 2^{- "
                r"\tmp{u}} + 3 \tmp{u} \cdot 4^{- \tmp{u}} - 8^{- \tmp{u}},$$ without the cancellation "
                "that makes the published function exactly 0 at many x-values next to the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

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
