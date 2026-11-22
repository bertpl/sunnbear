"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Romadani202551(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``x^7 - 2*x^6 + 4*x^5 - 1``; the formula's interval is ``[0, 1]``.

    Eq. (8). Stated root `0.800631154473`.
    """

    number = (1, 2, 17, 1)
    name = "5.1"
    params = ()
    location_in_publication = "Section 5.1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{7} - 2 \tmp{u}^{6} + 4 \tmp{u}^{5} - 1",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**7 - 2 * x**6 + 4 * x**5 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.9915193),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.99999878046875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
