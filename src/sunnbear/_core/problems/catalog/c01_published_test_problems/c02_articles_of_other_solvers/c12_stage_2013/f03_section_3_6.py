"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Stage2013Section36(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``1 - (3/4)*x``; the formula's interval is ``[-10, 10]``.

    The root is `4/3`, outside the range that §3.2 states for all functions.
    """

    number = (1, 2, 12, 3)
    name = "Section 3.6"
    params = ()
    location_in_publication = "§3.6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"1 - \frac{3 \tmp{u}}{4}",
        interval="[-10, 10]",
        summary="A straight line with 1 root, slightly above the middle of the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return 1 - (3 / 4) * x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=4.0),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=7.75),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
