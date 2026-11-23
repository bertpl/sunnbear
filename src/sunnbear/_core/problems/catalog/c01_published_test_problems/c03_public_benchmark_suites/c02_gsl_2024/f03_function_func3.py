"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Gsl2024FunctionFunc3(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x^2 - 1e-8``; the formula's interval is ``[0, 1]``.

    Starting point 1; derivative given
    """

    number = (1, 3, 2, 3)
    name = "Function func3"
    params = ()
    location_in_publication = "test_funcs.c, func3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - 1.0 \cdot 10^{-8}",
        interval="[0, 1]",
        summary=(
            r"A parabola with its minimum at the lower bound, negative only over the first $10^{-4}$ of the "
            r"interval and there no lower than $-10^{-8}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 1e-8

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.08999998999999999),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.002499989999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
