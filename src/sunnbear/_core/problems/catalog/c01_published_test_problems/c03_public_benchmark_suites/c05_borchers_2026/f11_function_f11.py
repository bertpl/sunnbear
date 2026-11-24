"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f11`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF11(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x^9 + 0.0001``; the formula's interval is ``[-1.2, 0]``.

    Printed root: `-0.3593813664`
    """

    number = (1, 3, 5, 11)
    name = "Function f11"
    params = ()
    location_in_publication = "§5.6, f11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.2 \c"),),
        expression=r"\tmp{u}^{9} + 0.0001",
        interval="[-1.2, 0]",
        summary=(
            "A 9th power plus $10^{-4}$, with 1 root, and values below $10^{-4}$ in magnitude from just below that root"
            " to 0.36 above it."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return x**9 + 0.0001

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.2, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.84, c=0.0, expected=-0.2081157485309296),
        FormulaTestCase.value(params={}, x=-0.84, c=0.25, expected=-3.2518485211566346),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.2, 0.0)),
    )
