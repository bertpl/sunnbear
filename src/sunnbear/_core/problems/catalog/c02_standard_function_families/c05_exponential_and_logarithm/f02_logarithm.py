"""This formula is the logarithm next to its singularity at 0, ``2*log(x)/log(1/d) + 1 + c``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamNotation, ParamRecipe


class Logarithm(Formula):
    """`Logarithm` is ``2*log(x)/log(1/d) + 1 + c`` on ``[d, 1]``.

    ``log`` has a singularity at 0. ``d`` is its distance from the lower bound of the interval, between 0 and 1. For a
    ``d`` close to 1 the function is close to a line, and for a small ``d`` it is steep next to the lower bound and
    flat over most of the interval.

    The division by ``log(1/d)`` makes the function -1 at the lower bound and 1 at the upper bound at ``c = 0``, for
    every ``d``.

    ``c`` adds to the function value, so the root lies at ``x = d^((1 + c)/2)``: at ``sqrt(d)`` for ``c = 0``, and
    closer to the singularity for a larger ``c``.

    References:
        - NIST Digital Library of Mathematical Functions, §4.2, for the definition. https://dlmf.nist.gov/4.2
    """

    number = (2, 5, 2)
    name = "Logarithm"
    param_names = ("d",)

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``2*log(x)/log(1/d) + 1 + c``."""
        return 2.0 * math.log(x) / math.log(1.0 / d) + 1.0 + c

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[d, 1]``."""
        return (d, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``d`` from 10^-15 to 10^-0.1.

        The recipe does not leave out the candidates that fail the benchmark suite inclusion conditions. For the
        smallest ``d``, the range of ``c`` lets the root come too close to the lower bound to satisfy the conditions,
        so no benchmark suite holds such a candidate.
        """
        return (ParamGrid(axes=(ParamAxis("d", -15.0, -0.1, 0.1, ParamNotation.POW10),)),)

    def is_param_tuple_valid(self, d: float) -> bool:
        """Require ``d`` to be between 0 and 1."""
        return 0.0 < d < 1.0

    test_cases = (
        FormulaTestCase.value(params={"d": 0.01}, x=0.1, c=0.0, expected=0.0),  # the root at c = 0, at sqrt(d)
        FormulaTestCase.value(params={"d": 0.01}, x=0.01, c=0.0, expected=-1.0),
        FormulaTestCase.value(params={"d": 0.01}, x=1.0, c=0.0, expected=1.0),
        FormulaTestCase.value(params={"d": 0.01}, x=0.01, c=0.2, expected=-0.8),  # c adds to the value
        FormulaTestCase.value(params={"d": 0.01}, x=0.01**0.6, c=0.2, expected=0.0),  # the root, at d^((1 + c)/2)
        FormulaTestCase.invalid(params={"d": 0.0}),
        FormulaTestCase.invalid(params={"d": 1.0}),
        FormulaTestCase.interval_bounds(params={"d": 0.01}, expected=(0.01, 1.0)),
    )
