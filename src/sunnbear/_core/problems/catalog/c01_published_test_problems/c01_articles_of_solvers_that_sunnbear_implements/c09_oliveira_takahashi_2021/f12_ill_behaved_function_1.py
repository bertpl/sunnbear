"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction1(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x*10^6 - 1)^3``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 12)
    name = "Ill-behaved function 1"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u} \cdot 10^{6} - 1\right)^{3}",
        interval="[-1, 1]",
        summary="A cube with a triple root and a magnitude of $10^{18}$ at a distance of 1 from that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x * 10**6 - 1) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-6.400048000120001e16),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=-7.290024300027e17),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
