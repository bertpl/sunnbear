"""This module holds a formula of Gottlieb, Thompson (2010).

The formula comes from the row with the key ``7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GottliebThompson2010Test7(Formula):
    """This formula comes from Gottlieb, Thompson (2010).

    The survey writes the source's function as ``1/x - 1``; the formula's interval is ``[0.5, 2.0]``.

    Table 2's root `1.0000000000`.
    """

    number = (1, 2, 8, 3)
    name = "Test 7"
    params = ()
    location_in_publication = "Table 1, test 7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\frac{1}{\tmp{u}} - 1",
        interval="[0.5, 2]",
        summary=(
            "A hyperbola, steep near the lower bound because of the pole 0.5 below that bound, with 1 root at a third "
            "of the interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return 1 / x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.95, c=0.0, expected=0.052631578947368474),
        FormulaTestCase.value(params={}, x=0.95, c=0.25, expected=0.7391304347826089),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 2.0)),
    )
