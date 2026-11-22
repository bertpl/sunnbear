"""This module holds a formula of Tomov, Ganchovski (2026).

The formula comes from the row with the key ``7.6-b`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class TomovGanchovski2026FunctionB(Formula):
    """This formula comes from Tomov, Ganchovski (2026).

    The survey writes the source's function as ``x - 1/4``; the formula's interval is endpoint pairs `(1/4, 1)` and `(1,
    1/4)`.

    The solver must return the endpoint root. The second pair gives the endpoints in reversed order.
    """

    number = (1, 1, 15, 2)
    name = "Function b"
    params = ()
    location_in_publication = "Section 7.6, function b"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.75 \c"),),
        expression=r"\tmp{u} - \frac{1}{4}",
        interval="[0.25, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.75 * c
        return x - 1 / 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.25, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.475, c=0.0, expected=0.22499999999999998),
        FormulaTestCase.value(params={}, x=0.475, c=0.25, expected=0.03749999999999998),
        FormulaTestCase.interval_bounds(params={}, expected=(0.25, 1.0)),
    )
