"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF3(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``35*x^35 - 1``; the formula's interval is ``[-0.5, 1.9]``.

    Printed root: `0.9034076632`
    """

    number = (1, 3, 5, 3)
    name = "Function f3"
    params = ()
    location_in_publication = "§5.6, f3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.4 \c"),),
        expression=r"35 \tmp{u}^{35} - 1",
        interval="[-0.5, 1.9]",
        summary=(
            r"A 35th power minus 1, with 1 root, steep toward the upper bound, and exactly $-1$ in floating point on a "
            r"band 0.63 wide centered on $\x = 2.4 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.4 * c
        return 35 * x**35 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 1.9)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.18, c=0.0, expected=11478.905156430781),
        FormulaTestCase.value(params={}, x=1.18, c=0.25, expected=-0.9999998163259429),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 1.9)),
    )
