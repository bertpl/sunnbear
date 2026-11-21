"""This formula is a signed power shifted up or down by ``c``, ``sign(x)*abs(x)^p + c``."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamGrid,
    ParamRecipe,
)

from .helpers import power_axis


class SignedPower2(Formula):
    """`SignedPower2` is ``sign(x)*abs(x)^p + c`` on ``[-1, 1]``.

    The signed power ``sign(x)*abs(x)^p`` is the power of `SignedPower1`, whose class docstring describes it. At
    ``x = 0`` its slope is infinite below ``p = 1`` and 0 above ``p = 1``.

    ``p`` is the power, any value above 0.

    ``c`` adds to the function value, while in `SignedPower1` ``c`` shifts x. The root then lies at
    ``-sign(c)*abs(c)^(1/p)``, away from 0, and it is a simple root for every ``c`` but 0.

    The infinite or zero slope stays at ``x = 0``, away from the root, so a solver may evaluate f near 0 before it
    reaches the root.

    At ``c = 0`` the function passes through ``(-1, -1)`` and ``(1, 1)`` for every ``p``, so the calibrated range of
    ``c`` is the same for all of the formula's test problems.
    """

    number = (2, 3, 2)
    name = "Signed power 2"
    params = (FormulaParam("p", latex_symbol="p"),)
    presentation = FormulaPresentation(
        expression=r"\operatorname{sgn}(\x) \, |\x|^{\param{p}} + \c",
        interval="[-1, 1]",
        summary=r"A signed power, whose infinite or zero slope at $\x = 0$ lies away from its root.",
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float) -> float:
        """Evaluate ``sign(x)*abs(x)^p + c``."""
        return math.copysign(abs(x) ** p, x) + c

    def interval_bounds(self, p: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``p`` from 10^-6 to 10^6, the sweep of `SignedPower1`.

        At the low end the function is close to the step ``sign(x) + c``, and its root lies next to 0. At the high end
        the function equals ``c`` on nearly all of the interval, and its root lies next to a bound.
        """
        return (
            ParamGrid(axes=(power_axis(-6.0, 6.0),), summary=r"The sweep of $\param{p}$ from $10^{-6}$ to $10^{6}$."),
        )

    def is_param_tuple_valid(self, p: float) -> bool:
        """Require ``p`` to be above 0."""
        return p > 0.0

    test_cases = (
        FormulaTestCase.value(params={"p": 2.0}, x=0.5, c=0.0, expected=0.25),
        FormulaTestCase.value(params={"p": 2.0}, x=-0.5, c=0.0, expected=-0.25),  # the sign of x
        FormulaTestCase.value(params={"p": 0.5}, x=0.25, c=0.1, expected=0.6),  # c shifts the value
        FormulaTestCase.value(params={"p": 0.5}, x=-0.25, c=0.5, expected=0.0),  # the root, at -abs(c)^(1/p)
        FormulaTestCase.invalid(params={"p": 0.0}),
        FormulaTestCase.invalid(params={"p": -2.0}),
        FormulaTestCase.interval_bounds(params={"p": 2.0}, expected=(-1.0, 1.0)),
    )
