"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``38`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem38(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 + 2*x^3 - 13*x^2 - 14*x + 24``; the formula's interval is ``[-3,
    1]``.
    """

    number = (1, 2, 18, 20)
    name = "Problem 38"
    params = ()
    location_in_publication = "dataset.json, problem 38"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{4} + 2 \tmp{u}^{3} - 13 \tmp{u}^{2} - 14 \tmp{u} + 24",
        interval="[-3, 1]",
        summary=(
            r"The quartic $(\tmp{u} + 4)(\tmp{u} + 2)(\tmp{u} - 1)(\tmp{u} - 3)$ written out as a polynomial, with 1 "
            r"root inside the interval and another at $\x = 1 + 10 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**4 + 2 * x**3 - 13 * x**2 - 14 * x + 24

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.8, c=0.0, expected=5.913599999999999),
        FormulaTestCase.value(params={}, x=-1.8, c=0.1, expected=-21.158399999999997),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 1.0)),
    )
