"""This formula is the inverse hyperbolic tangent between its 2 poles, ``atanh(x)/atanh(1 - d) + c``."""

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


class InverseHyperbolicTangent(Formula):
    """`InverseHyperbolicTangent` is ``atanh(x)/atanh(1 - d) + c`` on ``[-(1 - d), 1 - d]``.

    ``atanh`` has a pole at -1 and at 1, where it grows as a logarithm: next to 1, ``atanh(1 - t)`` is about
    ``log(2/t)/2``.

    ``d`` is the distance from each pole to the nearest bound of the interval, between 0 and 1. For a ``d`` close to 1
    the function is close to a line, and for a small ``d`` it is steep next to both bounds.

    The division by ``atanh(1 - d)`` makes the function -1 at the lower bound and 1 at the upper bound at ``c = 0``, for
    every ``d``.

    ``c`` adds to the function value, so the root lies at ``x = -tanh(c*atanh(1 - d))``.

    References:
        - NIST Digital Library of Mathematical Functions, §4.37, for the definition. https://dlmf.nist.gov/4.37
    """

    number = (2, 4, 6)
    name = "Inverse hyperbolic tangent"
    params = (
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=r"The distance from each pole of $\operatorname{artanh}$, at $-1$ and $1$, to the nearest bound.",
        ),
    )
    presentation = FormulaPresentation(
        expression=r"\frac{\operatorname{artanh} \x}{\operatorname{artanh}(1 - \param{d})} + \c",
        interval=r"[-(1 - \param{d}), 1 - \param{d}]",
        summary=(
            r"The inverse hyperbolic tangent, steep next to both bounds for a small $\param{d}$, where they lie close "
            "to its poles."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``atanh(x)/atanh(1 - d) + c``."""
        return math.atanh(x) / math.atanh(1.0 - d) + c

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[-(1 - d), 1 - d]``."""
        return (-(1.0 - d), 1.0 - d)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``d`` from 10^-15 to 10^-1.

        The recipe does not leave out the candidates that fail the benchmark suite inclusion conditions. For the
        smallest ``d``, the range of ``c`` lets the root come too close to a bound to satisfy the conditions, so no
        benchmark suite holds such a candidate.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("d", -15.0, -1.0, 0.1, ParamNotation.POW10),),
                summary=r"The sweep of $\param{d}$ from $10^{-15}$ to $10^{-1}$.",
            ),
        )

    def is_param_tuple_valid(self, d: float) -> bool:
        """Require ``d`` to be between 0 and 1."""
        return 0.0 < d < 1.0

    test_cases = (
        FormulaTestCase.value(params={"d": 0.1}, x=0.0, c=0.0, expected=0.0),  # the root at c = 0
        FormulaTestCase.value(params={"d": 0.1}, x=0.9, c=0.0, expected=1.0),
        FormulaTestCase.value(params={"d": 0.1}, x=-0.9, c=0.2, expected=-0.8),  # c adds to the value
        FormulaTestCase.value(params={"d": 0.1}, x=-math.tanh(0.5 * math.atanh(0.9)), c=0.5, expected=0.0),
        FormulaTestCase.invalid(params={"d": 0.0}),
        FormulaTestCase.invalid(params={"d": 1.0}),
        FormulaTestCase.interval_bounds(params={"d": 0.1}, expected=(-0.9, 0.9)),
    )
