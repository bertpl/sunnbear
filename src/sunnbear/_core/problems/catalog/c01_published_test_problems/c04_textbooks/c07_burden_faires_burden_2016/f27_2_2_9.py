"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.2-9`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016229(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = pi + 0.5*sin(x/2)``; the formula's interval is ``[0, 2*pi]``.

    Unique fixed point on the interval by Theorem 2.3. Fixed-point iteration to `1E-2`, and Corollary 2.5's bound on the
    number of iterations compared with the number needed.
    """

    number = (1, 4, 7, 27)
    name = "2.2-9"
    params = ()
    location_in_publication = "Exercise 2.2-9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 6.28 \c"),),
        expression=r"\tmp{u} - \left(\pi + 0.5 \sin{\left(\frac{\tmp{u}}{2} \right)}\right)",
        interval=r"[0, 2 \pi]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 6.28 * c
        return (x) - (math.pi + 0.5 * math.sin(x / 2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 6.283185307179586)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.88496, c=0.0, expected=-1.661141798493021),
        FormulaTestCase.value(params={}, x=1.88496, c=0.25, expected=-2.905047598902962),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 6.283185307179586)),
    )
