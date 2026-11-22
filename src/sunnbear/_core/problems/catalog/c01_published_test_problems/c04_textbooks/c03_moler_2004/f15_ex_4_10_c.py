"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.10(c)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import bessel_j0, bessel_y0


class Moler2004Ex410C(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``J0(x) = Y0(x)``; the formula's interval is ``[0, 10*pi]``.

    All solutions between 0 and `10*pi`.
    """

    number = (1, 4, 3, 15)
    name = "Ex. 4.10(c)"
    params = ()
    location_in_publication = "Exercise 4.10(c)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 31.4 \c"),),
        expression=r"J_{0}\left(\tmp{u}\right) - Y_{0}\left(\tmp{u}\right)",
        interval=r"[0, 10 \pi]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 31.4 * c
        return (bessel_j0(x)) - (bessel_y0(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 31.41592653589793)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=9.42478, c=0.0, expected=-0.36726657736486834),
        FormulaTestCase.value(params={}, x=9.42478, c=0.25, expected=0.05828461127689465),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 31.41592653589793)),
    )
