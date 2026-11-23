"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem510(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^4 - 8*x^3 - 35*x^2 + 450*x - 1001``; the formula's interval is
    ``[4.5, 6]``.

    Positive real root 5.60979, as the book states; 5 false-position iterations, a plot to explain the result, then
    false position to `es = 1.0%`.
    """

    number = (1, 4, 6, 18)
    name = "Problem 5.10"
    params = ()
    location_in_publication = "Prob. 5.10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\tmp{u}^{4} - 8 \tmp{u}^{3} - 35 \tmp{u}^{2} + 450 \tmp{u} - 1001",
        interval="[4.5, 6]",
        summary=(
            "A quartic with 1 simple root on the interval and, left of that root, a local maximum of $-1$ and a local "
            "minimum only 0.12 lower."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return x**4 - 8 * x**3 - 35 * x**2 + 450 * x - 1001

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.5, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.95, c=0.0, expected=-1.0139937499999998),
        FormulaTestCase.value(params={}, x=4.95, c=0.25, expected=-2.791687109374998),
        FormulaTestCase.interval_bounds(params={}, expected=(4.5, 6.0)),
    )
