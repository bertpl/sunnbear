"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``Fig. 1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Sabharwal2019Figure1(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``4 - (x - 1)^3``; the formula's interval is ``[1.00, 4.00]``.

    In Figure 1's run of the false position method, the right endpoint stays fixed. The root is `1 + 4^(1/3)`.
    """

    number = (1, 2, 13, 1)
    name = "Figure 1"
    params = ()
    location_in_publication = "Fig. 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"4 - \left(\tmp{u} - 1\right)^{3}",
        interval="[1, 4]",
        summary=(
            "A cubic with a stationary inflection point at the lower bound, decreasing and concave on the interval, "
            "with 1 simple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return 4 - (x - 1) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.9, c=0.0, expected=3.2710000000000004),
        FormulaTestCase.value(params={}, x=1.9, c=0.25, expected=3.996625),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 4.0)),
    )
