"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``T2.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Gao2026Table2Function2(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``x^7``; the formula's interval is ``[-3, 5]``.

    Also named in Section 3's opening paragraphs.
    """

    number = (1, 1, 14, 4)
    name = "Table 2, function 2"
    params = ()
    location_in_publication = "Table 2, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{7}",
        interval="[-3, 5]",
        summary="A 7th power, below $10^{-4}$ in magnitude within 0.26 of its root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.6, c=0.0, expected=-0.027993599999999993),
        FormulaTestCase.value(params={}, x=-0.6, c=0.2, expected=-803.1810176000002),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 5.0)),
    )
