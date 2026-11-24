"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.11-25`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Exercise31125(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(x - 1)^5``; the formula's interval is ``[0.998, 1.002]``.

    Evaluated at 400 points in 3 forms: `(x - 1)^5`, `x^5 - 5*x^4 + 10*x^3 - 10*x^2 + 5*x - 1` and `-1 + x*(5 + x*(-10 +
    x*(10 + x*(-5 + x))))`.
    """

    number = (1, 4, 5, 23)
    name = "Exercise 3.11-25"
    params = ()
    location_in_publication = "Exercise 3.11-25"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.004 \c"),),
        expression=r"\left(\tmp{u} - 1\right)^{5}",
        interval="[0.998, 1.002]",
        summary=(
            r"A 5th power that stays below $4 \cdot 10^{-14}$ in magnitude within 0.002 of its root, and yet has the "
            r"correct computed sign everywhere."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.004 * c
        return (x - 1) ** 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.998, 1.002)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={}, x=0.9992, c=0.0, expected=-3.276800000000469e-16, atol=0.0),
        FormulaTestCase.value(params={}, x=0.9992, c=0.25, expected=-1.8895680000001248e-14, atol=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.998, 1.002)),
    )
