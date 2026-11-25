"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``Fig. 2.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Figure22(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``(x - 1)^7``; the formula's interval is `[0, 2]` (Fig. 2.2).

    Root 1. Figure only, plotted on `[0, 2]`: its flat plateau means that `abs(f) < 1E-7` only guarantees `x` within
    `1E-1` of the root.
    """

    number = (1, 4, 4, 4)
    name = "Figure 2.2"
    params = ()
    location_in_publication = "Fig. 2.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u} - 1\right)^{7}",
        interval="[0, 2]",
        summary=(
            "A function flat at its root of multiplicity 7 and below $10^{-7}$ in magnitude within 0.1 of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x - 1) ** 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.0016384000000000006),
        FormulaTestCase.value(params={}, x=0.6, c=0.5, expected=-0.4782969000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
