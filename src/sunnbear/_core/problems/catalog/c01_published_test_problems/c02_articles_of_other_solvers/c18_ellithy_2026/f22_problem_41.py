"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``41`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem41(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(x + 0.3)^7 - 0.01``; the formula's interval is ``[-2, 1]``.
    """

    number = (1, 2, 18, 22)
    name = "Problem 41"
    params = ()
    location_in_publication = "dataset.json, problem 41"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\left(\tmp{u} + 0.3\right)^{7} - 0.01",
        interval="[-2, 1]",
        summary=(
            r"A 7th power, nearly flat around $\x = 3 \c - 0.3$, with 1 root and values below 0.02 in magnitude over "
            r"37% of the interval around that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (x + 0.3) ** 7 - 0.01

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.0, expected=-0.21971520000000017),
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=-21.504229774218757),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
