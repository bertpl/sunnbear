"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``(23)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021Equation23(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x - (100 + 10*pi))*(x - 10*pi)``; the formula's interval is ``[-100,
    100]``.

    Appendix C, not in Table 1. The root is `x* = 10*pi`; the article solves it with `epsilon = 10^-50` at 1,000-bit
    precision. Not in sunnbear's transcription.
    """

    number = (1, 1, 9, 24)
    name = "Equation (23)"
    params = ()
    location_in_publication = "Appendix C, Eq. (23)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 200 \c"),),
        expression=r"\left(\tmp{u} - \left(100 + 10 \pi\right)\right) \left(\tmp{u} - 10 \pi\right)",
        interval="[-100, 100]",
        summary="A parabola with 2 simple roots 100 apart, only the lower of which lies on the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 200.0 * c
        return (x - (100 + 10 * math.pi)) * (x - 10 * math.pi)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-100.0, 100.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-40.0, c=0.0, expected=12241.827216570564),
        FormulaTestCase.value(params={}, x=-40.0, c=0.25, expected=26883.419870160356),
        FormulaTestCase.interval_bounds(params={}, expected=(-100.0, 100.0)),
    )
