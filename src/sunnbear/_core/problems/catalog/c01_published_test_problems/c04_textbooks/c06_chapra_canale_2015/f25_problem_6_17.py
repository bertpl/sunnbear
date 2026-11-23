"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 6.17`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem617(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``0.0074*x^4 - 0.284*x^3 + 3.355*x^2 - 12.183*x + 5``; the formula's
    interval is ``[15, 20]``.

    A real root between 15 and 20, as the book states; Newton from `x0 = 16.15`, and an explanation of the result.
    """

    number = (1, 4, 6, 25)
    name = "Problem 6.17"
    params = ()
    location_in_publication = "Prob. 6.17"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"0.0074 \tmp{u}^{4} - 0.284 \tmp{u}^{3} + 3.355 \tmp{u}^{2} - 12.183 \tmp{u} + 5",
        interval="[15, 20]",
        summary=(
            "A quartic with 4 real roots, on an interval that holds the largest one and a local minimum left of that "
            "root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return 0.0074 * x**4 - 0.284 * x**3 + 3.355 * x**2 - 12.183 * x + 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (15.0, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=16.5, c=0.0, expected=-9.8957875),
        FormulaTestCase.value(params={}, x=16.5, c=0.25, expected=-7.54040859375),
        FormulaTestCase.interval_bounds(params={}, expected=(15.0, 20.0)),
    )
