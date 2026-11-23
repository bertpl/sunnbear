"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Stage2013Section310(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``(x - 7/9)^3 + 0.001*(x - 7/9)``; the formula's interval is ``[-10,
    10]``.

    The subsection title reads "Testing an Cubic Polynomial Function".
    """

    number = (1, 2, 12, 7)
    name = "Section 3.10"
    params = ()
    location_in_publication = "§3.10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\left(\tmp{u} - \frac{7}{9}\right)^{3} + 0.001 \left(\tmp{u} - \frac{7}{9}\right)",
        interval="[-10, 10]",
        summary="A cubic plus a small linear term, increasing, with a simple root where its slope is only $10^{-3}$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return (x - 7 / 9) ** 3 + 0.001 * (x - 7 / 9)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=-109.06787791495199),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=-934.8136186556927),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
