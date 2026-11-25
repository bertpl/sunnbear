"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-17`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Exercise2117(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``cos(4*zeta*sqrt(1 - zeta^2)) = -1 + 8*zeta^2 - 8*zeta^4``; the
    formula's interval is ``(0, 1/2)``.

    Unknown `zeta`, the nondimensional damping coefficient, to `5E-7`; the exercise then computes the maximum force from
    it.
    """

    number = (1, 4, 4, 22)
    name = "Exercise 2.1-17"
    params = ()
    location_in_publication = "Exercise 2.1-17"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\cos{\left(4 \tmp{u} \sqrt{1 - \tmp{u}^{2}} \right)} - \left(-1 + 8 "
            r"\tmp{u}^{2} - 8 \tmp{u}^{4}\right)"
        ),
        interval="[0, 0.5]",
        summary=(
            r"A function symmetric about its maximum at $\x = \c$, decreasing from that maximum to 1 simple root "
            r"0.40 above the maximum."
        ),
        notes=(r"$\tmp{u}$ is the source's variable $\zeta$, the nondimensional damping coefficient.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (math.cos(4 * x * math.sqrt(1 - x**2))) - (-1 + 8 * x**2 - 8 * x**4)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.15, c=0.0, expected=1.6531995889164552),
        FormulaTestCase.value(params={}, x=0.15, c=0.125, expected=1.990010410073922),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 0.5)),
    )
