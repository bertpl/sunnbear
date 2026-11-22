"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-2; §2.3 (p. 86), Table 2.4; 2.2-4; 2.4-3; 2.5-5`` in the survey of
published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Exercise212(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^3 + x^2 - 3*x - 3``; the formula's interval is ``(1, 2)``.

    Root `sqrt(3)` in the interval; -1 and `-sqrt(3)` lie outside it. Bisection (2.1-2), false position (2.2-4), Newton
    (2.4-3) and secant (2.5-5). Table 2.4 runs fixed-point iteration from `p0 = 1` to `1E-7` with 5 iteration functions:
    `g1 = (x^3 + x^2 - 3)/3`, which converges to -1; `g2 = -1 + (3*x + 3)/x^2`, which does not converge; `g3 = (3 + 3*x
    - x^2)^(1/3)`; `g4 = sqrt((3 + 3*x - x^2)/x)`; and `g5 = x - (x^3 + x^2 - 3*x - 3)/(3*x^2 + 2*x - 3)`.
    """

    number = (1, 4, 4, 12)
    name = "Exercise 2.1-2"
    params = ()
    location_in_publication = "Exercise 2.1-2; §2.3 (p. 86), Table 2.4; Exercises 2.2-4, 2.4-3, 2.5-5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} + \tmp{u}^{2} - 3 \tmp{u} - 3",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + x**2 - 3 * x - 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-3.013),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-3.889875),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
