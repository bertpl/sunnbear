"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``26`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem26(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^5 - 3*x^4 + 25``; the formula's interval is ``[-3, -1]``.
    """

    number = (1, 2, 18, 11)
    name = "Problem 26"
    params = ()
    location_in_publication = "dataset.json, problem 26"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{5} - 3 \tmp{u}^{4} + 25",
        interval="[-3, -1]",
        summary=(
            "A quintic with 1 root and, 1.53 above that root, a local maximum of 25 at which the first 3 derivatives "
            "vanish."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**5 - 3 * x**4 + 25

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, -1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-2.4, c=0.0, expected=-154.15903999999998),
        FormulaTestCase.value(params={}, x=-2.4, c=0.5, expected=-392.29578999999995),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, -1.0)),
    )
