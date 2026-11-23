"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f8`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF8(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``1/8*(9 - 1/x)``; the formula's interval is ``[0.001, 1.201]``.

    Printed root: `0.1111111111`
    """

    number = (1, 3, 5, 8)
    name = "Function f8"
    params = ()
    location_in_publication = "§5.6, f8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.2 \c"),),
        expression=r"\frac{9 - \frac{1}{\tmp{u}}}{8}",
        interval="[0.001, 1.201]",
        summary=(
            r"A hyperbola with 1 root, steep next to the lower bound, close to its pole at $\x = 0$, and nearly flat "
            r"over the upper half."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return 1 / 8 * (9 - 1 / x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.001, 1.201)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.361, c=0.0, expected=0.7787396121883656),
        FormulaTestCase.value(params={}, x=0.361, c=0.25, expected=-0.9241803278688525),
        FormulaTestCase.interval_bounds(params={}, expected=(0.001, 1.201)),
    )
