"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``(2.7.3); P38(b)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Atkinson1989Equation273(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^4 - 5.4*x^3 + 10.56*x^2 - 8.954*x + 2.7951``; the formula's interval
    is `[1, 1.2]` (P38(b)).

    Printed also as `(x - 1.1)^3*(x - 2.1)`; (2.7.4) gives the nested form `2.7951 + x*(-8.954 + x*(10.56 + x*(-5.4 +
    x)))`. Table 2.10 evaluates both forms in double precision near `x = 1.1`: at most 6 digits of the root 1.1 are
    attainable. P38(b) measures the noise in steps of `h = 0.001`; P41 finds the roots.
    """

    number = (1, 4, 1, 3)
    name = "Equation (2.7.3)"
    params = ()
    location_in_publication = "Eq. (2.7.3); Problem 38(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.2 \c"),),
        expression=r"\tmp{u}^{4} - 5.4 \tmp{u}^{3} + 10.56 \tmp{u}^{2} - 8.954 \tmp{u} + 2.7951",
        interval="[1, 1.2]",
        summary=(
            r"$(\x - 1.1)^3 (\x - 2.1)$ written out as a polynomial, whose computed sign is wrong at some points within"
            r" $1.5 \cdot 10^{-5}$ of the triple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.2 * c
        return x**4 - 5.4 * x**3 + 10.56 * x**2 - 8.954 * x + 2.7951

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 1.2)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.06, c=0.0, expected=6.655999999999973e-05),
        FormulaTestCase.value(params={}, x=1.06, c=0.25, expected=0.0007946099999999997),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 1.2)),
    )
