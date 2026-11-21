"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``T2.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Gao2026T21(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``x^5``; the formula's interval is ``[-1, 3]``.

    Vanishing derivative at the root. Also named in the introduction.
    """

    number = (1, 1, 14, 3)
    name = "T2.1"
    params = ()
    source = FormulaSource(
        reference=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied "
            "Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        location="Table 2, function 1",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\tmp{u}^{5}",
        interval="[-1, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.2, c=0.0, expected=0.0003200000000000001),
        FormulaTestCase.value(params={}, x=0.2, c=0.25, expected=-0.3276800000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 3.0)),
    )
