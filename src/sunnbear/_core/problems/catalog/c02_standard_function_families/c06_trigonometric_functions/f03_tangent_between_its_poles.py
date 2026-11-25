"""This formula is the tangent between its poles at -1 and 1, ``tan(0.5*pi*x)/tan(0.5*pi*(1 - d)) + c``."""

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


class TangentBetweenPoles(Formula):
    """`TangentBetweenPoles` is ``tan(0.5*pi*x)/tan(0.5*pi*(1 - d)) + c`` on ``[-(1 - d), 1 - d]``.

    The scale ``0.5*pi`` puts the poles of the tangent next to its zero at 0 at -1 and 1. ``d`` is the distance from
    each pole to the nearest bound, between 0 and 1. For a ``d`` close to 1 the function is close to a line; for a
    small ``d`` it is steep next to both bounds and flat between them.

    The division by ``tan(0.5*pi*(1 - d))`` makes the function -1 at the lower bound and 1 at the upper bound at
    ``c = 0``, for every ``d``.

    ``c`` adds to the function value, so the root moves from the inflection point at 0 toward a pole, to
    ``x = -(2/pi)*atan(c*tan(0.5*pi*(1 - d)))``. A shift of x would move a pole into the interval, and a scale of x
    would leave the root at 0.

    References:
        - NIST Digital Library of Mathematical Functions, §4.14, for the definition. https://dlmf.nist.gov/4.14
    """

    number = (2, 6, 3)
    name = "Tangent between its poles"
    params = (
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=r"The distance from each pole of the tangent, at $-1$ and $1$, to the nearest bound.",
        ),
    )
    presentation = FormulaPresentation(
        expression=r"\frac{\tan\left(\frac{\pi}{2} \x\right)}{\tan\left(\frac{\pi}{2} (1 - \param{d})\right)} + \c",
        interval=r"[-(1 - \param{d}), 1 - \param{d}]",
        summary=(
            r"The tangent between 2 poles just outside the interval, steep next to both bounds for a small $\param{d}$."
        ),
        param_conditions=(r"$0 < \param{d} < 1$",),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``tan(0.5*pi*x)/tan(0.5*pi*(1 - d)) + c``."""
        return math.tan(0.5 * math.pi * x) / math.tan(0.5 * math.pi * (1.0 - d)) + c

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[-(1 - d), 1 - d]``."""
        return (-(1.0 - d), 1.0 - d)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``d`` from 2^-30 to 2^-0.1.

        At ``d = 2^-0.1`` the interval is about ``[-0.067, 0.067]``, where the tangent is close to a line; at ``d = 1``
        the interval would be empty.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("d", -30.0, -0.1, 0.1, ParamNotation.POW2),),
                summary=r"The sweep of $\param{d}$ from $2^{-30}$ to $2^{-0.1}$.",
            ),
        )

    def is_param_tuple_valid(self, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return 0.0 < d < 1.0

    test_cases = (
        FormulaTestCase.value(params={"d": 0.25}, x=0.0, c=0.0, expected=0.0),  # the root at c = 0
        FormulaTestCase.value(params={"d": 0.25}, x=0.75, c=0.0, expected=1.0),
        FormulaTestCase.value(params={"d": 0.25}, x=-0.75, c=0.2, expected=-0.8),  # c adds to the value
        FormulaTestCase.value(
            params={"d": 0.25},
            x=-(2.0 / math.pi) * math.atan(0.5 * math.tan(0.375 * math.pi)),
            c=0.5,
            expected=0.0,
        ),
        FormulaTestCase.invalid(params={"d": 0.0}),
        FormulaTestCase.invalid(params={"d": 1.0}),
        FormulaTestCase.interval_bounds(params={"d": 0.25}, expected=(-0.75, 0.75)),
    )
