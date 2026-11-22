"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.9`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Stage201339(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``abs(x - 2/3)^0.2`` if ``x <= 2/3``; ``-abs(x - 2/3)^0.2`` otherwise;
    the formula's interval is ``[-10, 10]``.
    """

    number = (1, 2, 12, 6)
    name = "3.9"
    params = ()
    location_in_publication = "§3.9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\begin{cases} "
            r"|\tmp{u} - 2/3|^{0.2} & \text{if } \tmp{u} \le 2/3 \\ "
            r"-|\tmp{u} - 2/3|^{0.2} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-10, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        if x <= 2 / 3:
            return abs(x - 2 / 3) ** 0.2
        else:
            return -(abs(x - 2 / 3) ** 0.2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=1.3608221078587388),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=1.574183473407022),
        FormulaTestCase.value(params={}, x=5.0, c=0.0, expected=-1.3408012912084573),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
