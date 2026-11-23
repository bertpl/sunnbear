"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF2(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's interval is ``[0.4, 1.6]``.

    Printed root: `0.8041330975`
    """

    number = (1, 3, 5, 2)
    name = "Function f2"
    params = ()
    location_in_publication = "§5.6, f2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.2 \c"),),
        expression=r"11 \tmp{u}^{11} - 1",
        interval="[0.4, 1.6]",
        summary=(
            "An 11th power minus 1, with 1 root, nearly flat at $-1$ over the lower fifth of the interval and steep "
            "toward the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return 11 * x**11 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.4, 1.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.76, c=0.0, expected=-0.4625448852563808),
        FormulaTestCase.value(params={}, x=0.76, c=0.25, expected=-0.9978535101773714),
        FormulaTestCase.interval_bounds(params={}, expected=(0.4, 1.6)),
    )
