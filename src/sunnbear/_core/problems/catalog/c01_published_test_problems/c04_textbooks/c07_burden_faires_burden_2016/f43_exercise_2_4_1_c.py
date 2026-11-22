"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(c)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise241C(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 3*x^2*(2^-x) + 3*x*(4^-x) - 8^-x``; the formula's interval is
    ``[0, 1]``.

    As 2.4-1(a). It equals `(x - 2^-x)^3`, the cube of 2.1-5(a)'s function.
    """

    number = (1, 4, 7, 43)
    name = "Exercise 2.4-1(c)"
    params = ()
    location_in_publication = "Exercise 2.4-1(c)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\tmp{u}^{3} - 3 \tmp{u}^{2} \cdot 2^{- \tmp{u}} + 3 \tmp{u} \cdot 4^{- \tmp{u}} - 8^{- " r"\tmp{u}}"
        ),
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 3 * x**2 * (2**-x) + 3 * x * (4**-x) - 8**-x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.13441631843652777),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.7684150363472455),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
