"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f101`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ganchovski2026FunctionF101(Formula):
    """This formula comes from Ganchovski (2026).

    The survey writes the source's function as ``if(x < 0; -(x^2); 7*x^2)``; the formula's interval is ``[-3, 1]``.

    The root line uses `$Find`.
    """

    number = (1, 3, 4, 3)
    name = "Function f101"
    params = ()
    location_in_publication = "f101"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=(
            r"\begin{cases} - \tmp{u}^{2} & \text{for}\: \tmp{u} < 0 \\7 \tmp{u}^{2} & \text{otherwise} " r"\end{cases}"
        ),
        interval="[-3, 1]",
        summary=(
            "A piecewise quadratic that changes sign at its root despite a slope of 0 there, and is 7 times as "
            "steep above the root as below."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        if x < 0:
            return -(x**2)
        else:
            return 7 * x**2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.8, c=0.0, expected=-3.24),
        FormulaTestCase.value(params={}, x=-1.8, c=0.25, expected=-7.839999999999999),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=7.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 1.0)),
    )
