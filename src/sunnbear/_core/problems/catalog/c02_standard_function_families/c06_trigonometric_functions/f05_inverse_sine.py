"""This formula is the inverse sine between the edges of its domain, ``asin(x)/asin(1 - d) + c``."""

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


class InverseSine(Formula):
    """`InverseSine` is ``asin(x)/asin(1 - d) + c`` on ``[-(1 - d), 1 - d]``.

    ``asin`` is finite on its whole domain ``[-1, 1]``, and its slope is infinite at both edges: next to 1,
    ``asin(1 - t)`` is about ``pi/2 - sqrt(2*t)``.

    ``d`` is the distance from each edge of the domain to the nearest bound, at least 0 and below 1. At ``d = 0`` the
    interval is the whole domain, with the infinite slope at both bounds; for a ``d`` close to 1 the function is close
    to a line.

    The division by ``asin(1 - d)`` makes the function -1 at the lower bound and 1 at the upper bound at ``c = 0``, for
    every ``d``.

    ``c`` adds to the function value, so the root moves from the inflection point at 0 toward a bound, to
    ``x = -sin(c*asin(1 - d))``. A shift of x would move an edge of the domain into the interval, where ``asin`` is not
    defined.

    References:
        - NIST Digital Library of Mathematical Functions, §4.23, for the definition. https://dlmf.nist.gov/4.23
    """

    number = (2, 6, 5)
    name = "Inverse sine"
    params = (
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=r"The distance from each edge of the domain of $\arcsin$, at $-1$ and $1$, to the nearest bound.",
        ),
    )
    presentation = FormulaPresentation(
        expression=r"\frac{\arcsin(\x)}{\arcsin(1 - \param{d})} + \c",
        interval=r"[-(1 - \param{d}), 1 - \param{d}]",
        summary=(
            r"The inverse sine, steep next to both bounds for a small $\param{d}$, because both bounds then lie close "
            r"to the edges of its domain, where its slope is infinite."
        ),
        param_conditions=(r"$0 \le \param{d} < 1$",),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``asin(x)/asin(1 - d) + c``."""
        return math.asin(x) / math.asin(1.0 - d) + c

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[-(1 - d), 1 - d]``."""
        return (-(1.0 - d), 1.0 - d)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: ``d = 0``, the whole domain, and a sweep of ``d`` from 2^-30 to 2^-0.1.

        For a small ``d`` the function differs from the one at ``d = 0`` by about ``sqrt(2*d)``. At ``d = 2^-0.1`` the
        interval is about ``[-0.067, 0.067]``, where ``asin`` is close to a line.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("d", 0.0, 0.0, 1.0),), summary=r"$\param{d} = 0$, the whole domain of $\arcsin$."
            ),
            ParamGrid(
                axes=(ParamAxis("d", -30.0, -0.1, 0.1, ParamNotation.POW2),),
                summary=r"The sweep of $\param{d}$ from $2^{-30}$ to $2^{-0.1}$.",
            ),
        )

    def is_param_tuple_valid(self, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return 0.0 <= d < 1.0

    test_cases = (
        FormulaTestCase.value(params={"d": 0.0}, x=0.0, c=0.0, expected=0.0),  # the root at c = 0
        FormulaTestCase.value(params={"d": 0.0}, x=1.0, c=0.0, expected=1.0),  # the edge of the domain
        FormulaTestCase.value(params={"d": 0.0}, x=-1.0, c=0.2, expected=-0.8),  # c adds to the value
        FormulaTestCase.value(params={"d": 0.25}, x=-math.sin(0.5 * math.asin(0.75)), c=0.5, expected=0.0),
        FormulaTestCase.invalid(params={"d": -0.1}),
        FormulaTestCase.invalid(params={"d": 1.0}),
        FormulaTestCase.interval_bounds(params={"d": 0.25}, expected=(-0.75, 0.75)),
    )
