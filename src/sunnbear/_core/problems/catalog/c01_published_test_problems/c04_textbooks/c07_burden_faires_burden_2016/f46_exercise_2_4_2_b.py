"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-2(b)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise242B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^6 + 6*x^5 + 9*x^4 - 2*x^3 - 6*x^2 + 1``; the formula's interval is
    ``[-3, -2]``.

    As 2.4-2(a). The book prints the first term as `x^2`, a misprint: as printed, the function is negative on all of
    `[-3, -2]` and has no root there. With `x^6` it equals `(x^3 + 3*x^2 - 1)^2`, the square of 2.3-5(b)'s function,
    with a double root at -2.879385.
    """

    number = (1, 4, 7, 46)
    name = "Exercise 2.4-2(b)"
    params = ()
    location_in_publication = "Exercise 2.4-2(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{6} + 6 \tmp{u}^{5} + 9 \tmp{u}^{4} - 2 \tmp{u}^{3} - 6 \tmp{u}^{2} + 1",
        interval="[-3, -2]",
        summary=(
            r"The square of $\x^3 + 3\x^2 - 1$ written out, with a double root and rounding errors that turn the "
            r"function negative within $8 \cdot 10^{-8}$ of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**6 + 6 * x**5 + 9 * x**4 - 2 * x**3 - 6 * x**2 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, -2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-2.7, c=0.0, expected=1.4089689999999977),
        FormulaTestCase.value(params={}, x=-2.7, c=0.25, expected=0.3190837656250017),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, -2.0)),
    )
