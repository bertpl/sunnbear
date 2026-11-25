"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction6(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``1/(21*x - 1)``, with ``(x != 1/21)`` printed beside it; the formula's
    interval is ``[-1, 1]``.

    The formula returns 0 where the denominator ``21*x - 1`` is 0 in float64, which holds at 2 values of x: the float64
    value of ``1/21`` and the next float64 above it. The authors' code returns 0 only at the first, and divides by 0 at
    the second.
    """

    number = (1, 1, 9, 17)
    name = "Ill-behaved function 6"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } 21 \tmp{u} - 1 = 0 \\ "
            r"\frac{1}{21 \tmp{u} - 1} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-1, 1]",
        summary=(
            "A hyperbola that changes sign only at its pole, where the function is 0 only if the denominator is exactly"
            " 0 in floating point."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        denominator = 21 * x - 1
        if denominator == 0.0:
            return 0.0
        else:
            return 1 / denominator

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.10638297872340426),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=-0.05025125628140703),
        FormulaTestCase.value(params={}, x=1 / 21, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
