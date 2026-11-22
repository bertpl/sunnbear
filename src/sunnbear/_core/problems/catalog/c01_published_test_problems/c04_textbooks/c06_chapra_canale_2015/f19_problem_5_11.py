"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.11, 6.8, 7.10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem511(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^3.5 = 80``; the formula's interval is `[2.0, 5.0]` (5.11).

    Analytically and by false position to `es = 2.5%` (5.11); modified secant from `x0 = 3.5` with `delta = 0.01` to `es
    = 0.1%` (6.8); Excel, MATLAB or Mathcad (7.10).
    """

    number = (1, 4, 6, 19)
    name = "Problem 5.11"
    params = ()
    location_in_publication = "Prob. 5.11, 6.8, 7.10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\tmp{u}^{3.5} - 80",
        interval="[2, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (x**3.5) - (80)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.9, c=0.0, expected=-38.467029592142104),
        FormulaTestCase.value(params={}, x=2.9, c=0.25, expected=-65.42748168890004),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 5.0)),
    )
