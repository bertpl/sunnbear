"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem57(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``(0.8 - 0.3*x)/x``; the formula's interval is ``[1, 3]``.

    Root 8/3: analytically, graphically, and by 3 false-position iterations; the problem asks whether the result has a
    problem.
    """

    number = (1, 4, 6, 16)
    name = "Problem 5.7"
    params = ()
    location_in_publication = "Prob. 5.7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\frac{0.8 - 0.3 \tmp{u}}{\tmp{u}}",
        interval="[1, 3]",
        summary=(
            "A decreasing, convex hyperbola that stays below 0.034 in magnitude on a band 0.6 wide around the "
            "hyperbola's 1 simple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (0.8 - 0.3 * x) / x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=0.19999999999999998),
        FormulaTestCase.value(params={}, x=1.6, c=0.5, expected=0.4272727272727272),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
