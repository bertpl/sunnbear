"""This formula is the inverse hyperbolic sine on an interval around its root, ``asinh(x)/asinh(b) + c``."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
)


class InverseHyperbolicSine(Formula):
    """`InverseHyperbolicSine` is ``asinh(x)/asinh(b) + c`` on ``[-b, b]``.

    ``b`` is the upper bound of the interval, any value above 0. The function is close to a line for a small ``b``,
    and close to ``sign(x)*log(abs(x))``, up to a constant factor, for a large ``b``.

    The division by ``asinh(b)`` makes the function -1 at the lower bound and 1 at the upper bound at ``c = 0``, for
    every ``b``.

    ``c`` adds to the function value, so the root lies at ``x = sinh(-c*asinh(b))``. For a large ``b``, the root's
    distance from 0 spans many orders of magnitude across the range of ``c``.

    References:
        - NIST Digital Library of Mathematical Functions, §4.37, for the definition. https://dlmf.nist.gov/4.37
    """

    number = (2, 4, 4)
    name = "Inverse hyperbolic sine"
    params = (FormulaParam("b", latex_symbol="b"),)
    presentation = FormulaPresentation(
        expression=r"\frac{\operatorname{arsinh}(\x)}{\operatorname{arsinh}(\param{b})} + \c",
        interval=r"[-\param{b}, \param{b}]",
        summary="The inverse hyperbolic sine, close to a signed logarithm on a wide interval.",
        param_conditions=(r"$\param{b} > 0$",),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``asinh(x)/asinh(b) + c``."""
        return math.asinh(x) / math.asinh(b) + c

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^-1 to 10^15."""
        return (
            ParamGrid(
                axes=(ParamAxis("b", -1.0, 15.0, 0.1, ParamNotation.POW10),),
                summary=r"The sweep of $\param{b}$ from $10^{-1}$ to $10^{15}$.",
            ),
        )

    def is_param_tuple_valid(self, b: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 10.0}, x=0.0, c=0.0, expected=0.0),  # the root at c = 0
        FormulaTestCase.value(params={"b": 10.0}, x=10.0, c=0.0, expected=1.0),
        FormulaTestCase.value(params={"b": 10.0}, x=-10.0, c=0.2, expected=-0.8),  # c adds to the value
        FormulaTestCase.value(params={"b": 10.0}, x=math.sinh(-0.5 * math.asinh(10.0)), c=0.5, expected=0.0),
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 10.0}, expected=(-10.0, 10.0)),
    )
