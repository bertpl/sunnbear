"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction5(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x > (1 - 10^6)/10^6)*((1 + 10^6)/10^6) - 1``; the formula's interval
    is ``[-1, 1]``.
    """

    number = (1, 1, 9, 16)
    name = "Ill-behaved function 5"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\begin{cases} \frac{1 + 10^{6}}{10^{6}} & \text{for}\: \tmp{u} > \frac{1 - 10^{6}}{10^{6}}"
            r" \\0 & \text{otherwise} \end{cases} - 1"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (((1 + 10**6) / 10**6) if (x) > ((1 - 10**6) / 10**6) else 0.0) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=1e-06),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=1e-06),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
