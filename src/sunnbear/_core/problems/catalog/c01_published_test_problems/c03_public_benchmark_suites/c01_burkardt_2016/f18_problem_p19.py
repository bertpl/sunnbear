"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p19`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Burkardt2016ProblemP19(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``cos(100.0*x) - 4.0*erf(30.0*x - 10.0)``; the formula's interval is
    ``[0.0, 1.0]``.

    The source's starting points, in order, are `0.0`, `1.0` and `0.5`.
    """

    number = (1, 3, 1, 18)
    name = "Problem p19"
    params = ()
    location_in_publication = "Problem p19"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\cos{\left(100.0 \tmp{u} \right)} - 4.0 \operatorname{erf}{\left(30.0 \tmp{u} - 10.0 " r"\right)}"
        ),
        interval="[0, 1]",
        summary=(
            "A cosine with about 16 periods plus a smooth step from 4 to $-4$, with its 1 root in the step, referred to"
            ' in the source as "The jumping cosine".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.cos(100.0 * x) - 4.0 * math.erf(30.0 * x - 10.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=3.525054621686443),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=4.283662185463225),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
