"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Gsl2024FunctionFunc6(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``(x - 1)^7``; the formula's interval is ``[0.9995, 1.0002]``.

    Starting point 0.9, run by `steffenson` only; derivative given
    """

    number = (1, 3, 2, 5)
    name = "Function func6"
    params = ()
    location_in_publication = "test_funcs.c, func6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.0007 \c"),),
        expression=r"\left(\tmp{u} - 1\right)^{7}",
        interval="[0.9995, 1.0002]",
        summary="A 7th power on an interval so narrow that the function stays below $10^{-22}$ in magnitude there.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.0007 * c
        return (x - 1) ** 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.9995, 1.0002)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={}, x=0.99971, c=0.0, expected=-1.7249876309005193e-25, atol=0.0),
        FormulaTestCase.value(params={}, x=0.99971, c=0.25, expected=-4.700788051625088e-24, atol=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.9995, 1.0002)),
    )
