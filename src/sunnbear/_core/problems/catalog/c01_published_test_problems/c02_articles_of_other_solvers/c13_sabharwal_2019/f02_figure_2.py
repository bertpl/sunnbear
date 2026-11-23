"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``Fig. 2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Sabharwal2019Figure2(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``4 - (3 - x)^3``; the formula's interval is ``[0.20, 3.50]``.

    In Figure 2's run of the false position method, the left endpoint stays fixed. The root is `3 - 4^(1/3)`.
    """

    number = (1, 2, 13, 2)
    name = "Figure 2"
    params = ()
    location_in_publication = "Fig. 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3.3 \c"),),
        expression=r"4 - \left(3 - \tmp{u}\right)^{3}",
        interval="[0.2, 3.5]",
        summary=(
            "An increasing cubic with 1 simple root, steep at the lower bound and nearly flat around a stationary "
            "inflection point near the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.3 * c
        return 4 - (3 - x) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.2, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.19, c=0.0, expected=-1.9297410000000006),
        FormulaTestCase.value(params={}, x=1.19, c=0.25, expected=-14.295397875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.2, 3.5)),
    )
