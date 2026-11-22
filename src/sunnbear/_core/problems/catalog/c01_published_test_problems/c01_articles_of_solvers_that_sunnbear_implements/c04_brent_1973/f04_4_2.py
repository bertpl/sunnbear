"""This module holds a formula of Brent (1973).

The formula comes from the row with the key ``(4.2)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Brent197342(Formula):
    """This formula comes from Brent (1973).

    The survey writes the source's function as ``fl(exp(x))`` if ``x > -10^6``; ``fl(exp(-10^6) - (x + 10^6)^2)``
    otherwise. The formula's interval is ``[-1001200, 0]``, on which the book's procedure ``zero2`` solves with the
    absolute tolerance ``t = 1E-20``.

    ``fl(.)`` as in (4.1): the computed floating-point value. In float64, ``exp(x)`` underflows to 0 for x below about
    -745.13, so the formula is 0 on about ``[-10^6, -745.13]``.
    """

    number = (1, 1, 4, 4)
    name = "(4.2)"
    params = ()
    location_in_publication = "Section 4, Eq. (4.2)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10^{6} \c"),),
        expression=(
            r"\begin{cases} "
            r"e^{\tmp{u}} & \text{if } \tmp{u} > -10^{6} \\ "
            r"e^{-10^{6}} - (\tmp{u} + 10^{6})^2 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-1001200, 0]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1000000.0 * c
        if x > -1e6:
            return math.exp(x)
        else:
            return math.exp(-1e6) - (x + 1e6) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1001200.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.0, c=0.0, expected=0.36787944117144233),
        FormulaTestCase.value(params={}, x=-1000001.0, c=0.0, expected=-1.0),
        FormulaTestCase.value(params={}, x=-750300.0, c=0.25, expected=-90000.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1001200.0, 0.0)),
    )
