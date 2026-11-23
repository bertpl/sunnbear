"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Problem 3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class DowellJarratt1972Problem3(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``sum((-1)^n*x^((3*n^2 + n)/2), n = -inf..inf) - 1``; the formula's
    interval is ``[-0.9999, -0.0001]``.

    The formula sums the terms of ``n`` and ``-n`` together, from ``n = 1`` up, until adding them no longer changes the
    sum in float64, which happens for every x in ``(-1, 1)``; outside ``(-1, 1)``, where the series diverges, the
    formula is NaN.

    Defined for ``-1 < x < 1``. Root ``-0.679334``. Starting values ``x0 = -0.0001``, ``x1 = -0.9999``. The article
    calls it a well-behaved function.
    """

    number = (1, 1, 2, 4)
    name = "Problem 3"
    params = ()
    location_in_publication = "Problem 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sum_{n=-\infty}^{\infty} (-1)^n \tmp{u}^{(3n^2 + n)/2} - 1",
        interval="[-0.9999, -0.0001]",
        summary=(
            r"The Euler function $\prod_{k \ge 1} (1 - \x^k)$ minus 1, nearly flat at $-1$ next to the lower bound, "
            r"with 1 root and a second just past the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        if not -1.0 < x < 1.0:
            # the series diverges outside (-1, 1)
            return math.nan
        else:
            # the term of n = 0 is 1; then the terms of n and -n, from n = 1 up, until adding them no longer
            # changes the sum
            total = 1.0
            n = 1
            while True:
                term = (-1.0) ** n * (x ** ((3 * n * n - n) // 2) + x ** ((3 * n * n + n) // 2))
                if total + term == total:
                    return total - 1.0
                total += term
                n += 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.9999, -0.0001)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.69996, c=0.0, expected=-0.04892829857040081),
        FormulaTestCase.value(params={}, x=-0.69996, c=0.25, expected=-0.9973981399194692),
        FormulaTestCase.value(params={}, x=-0.9999, c=0.25, expected=math.nan),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.9999, -0.0001)),
    )
