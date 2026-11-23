"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Gsl2024FunctionFunc1(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x^20 - 1``; the formula's interval is ``[0.1, 2]``.

    Starting points 0.9, 1.1; derivative given
    """

    number = (1, 3, 2, 1)
    name = "Function func1"
    params = ()
    location_in_publication = "test_funcs.c, func1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.9 \c"),),
        expression=r"\tmp{u}^{20} - 1",
        interval="[0.1, 2]",
        summary=(
            "A polynomial of degree 20, nearly constant at $-1$ over the lower third of the interval and rising to "
            "about $10^6$ at the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.9 * c
        return x**20 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.67, c=0.0, expected=-0.9996677262338297),
        FormulaTestCase.value(params={}, x=1.43, c=0.25, expected=-0.6018310116739696),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 2.0)),
    )
