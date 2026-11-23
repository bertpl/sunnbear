"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``(2.1.2)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Atkinson1989Equation212(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^6 - x - 1``; the formula's interval is ``[1, 2]``.

    Largest real root `alpha = 1.13472413840152`. Bisection with `epsilon = 0.00005` (Table 2.1); Newton from `x0 = 2`
    (Table 2.2; the text also names `x0 = 1`); secant from `x0 = 2, x1 = 1` (Table 2.3). Section 2.9 (p. 95) applies
    Descartes's rule of signs to the same polynomial: 1 positive and 1 negative real root.
    """

    number = (1, 4, 1, 1)
    name = "Equation (2.1.2)"
    params = ()
    location_in_publication = "Eq. (2.1.2)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{6} - \tmp{u} - 1",
        interval="[1, 2]",
        summary="A sextic, steep toward the upper bound, with 1 simple root close to the lower bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**6 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=2.526809000000001),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.7099043593749997),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
