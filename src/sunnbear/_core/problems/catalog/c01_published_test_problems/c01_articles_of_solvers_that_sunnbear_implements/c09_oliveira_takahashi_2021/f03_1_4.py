"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi202114(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``4*x^5 + x^2 + 1``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 3)
    name = "1.4"
    params = ()
    location_in_publication = "Table 1, well-behaved function 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"4 \tmp{u}^{5} + \tmp{u}^{2} + 1",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 4 * x**5 + x**2 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=1.11904),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.5519600000000002),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
