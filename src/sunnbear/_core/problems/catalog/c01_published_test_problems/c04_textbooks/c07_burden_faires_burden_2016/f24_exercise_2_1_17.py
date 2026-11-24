"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-17; 2.2-8; 2.5-7; 2.6-1(c)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise2117(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - x - 1``; the formula's interval is ``[1, 2]``.

    Theorem 2.1's bound on the bisection iterations for `1E-4`, then the root (2.1-17); fixed-point iteration from `p0 =
    1` to `1E-2` (2.2-8); Steffensen's method to `1E-4` (2.5-7); all real zeros by Newton to `1E-4` (2.6-1).
    """

    number = (1, 4, 7, 24)
    name = "Exercise 2.1-17"
    params = ()
    location_in_publication = "Exercises 2.1-17, 2.2-8, 2.5-7, 2.6-1(c)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} - \tmp{u} - 1",
        interval="[1, 2]",
        summary=r"A cubic whose only real root lies at the plastic number plus $\c$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-0.10299999999999981),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.8923749999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
