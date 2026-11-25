"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021WellBehavedFunction5(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``x + x^10 - 1``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 4)
    name = "Well-behaved function 5"
    params = ()
    location_in_publication = "Table 1, well-behaved function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} + \tmp{u}^{10} - 1",
        interval="[-1, 1]",
        summary=(
            r"A line plus a 10th power that matters only near and beyond $\x = \c \pm 1$, with 1 simple root 0.16 "
            r"below $\x = \c + 1$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x + x**10 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-1.3998951424000001),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=-1.5513215598999999),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
