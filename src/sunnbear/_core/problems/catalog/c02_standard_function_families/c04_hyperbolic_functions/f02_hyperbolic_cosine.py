"""This formula is the hyperbolic cosine minus its value at the interval's midpoint, ``cosh(x - c) - cosh(b/2)``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamNotation, ParamRecipe


class HyperbolicCosine(Formula):
    """`HyperbolicCosine` is ``cosh(x - c) - cosh(b/2)`` on ``[0, b]``.

    ``b`` is the upper bound of the interval, any value above 0.

    ``cosh`` is even, with its minimum at 0, so ``cosh(x) - cosh(b/2)`` has 2 roots, ``-b/2`` and ``b/2``. The interval
    holds the minimum at its lower bound and the root ``b/2`` at its midpoint, so it holds an odd number of roots.

    The function is close to the parabola ``(x^2 - b^2/4)/2`` for a small ``b``, and grows as an exponential toward the
    upper bound for a large ``b``.

    ``c`` shifts x, so the minimum lies at ``x = c`` and the root at ``x = b/2 + c``. A positive ``c`` puts the minimum
    inside the interval, and a negative ``c`` makes the function increase over the whole interval.

    References:
        - NIST Digital Library of Mathematical Functions, §4.28, for the definition. https://dlmf.nist.gov/4.28
    """

    number = (2, 4, 2)
    name = "Hyperbolic cosine"
    param_names = ("b",)

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``cosh(x - c) - cosh(b/2)``."""
        return math.cosh(x - c) - math.cosh(0.5 * b)

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[0, b]``."""
        return (0.0, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^-1 to 10^2, with ``log10(b)`` in steps of 0.02.

        At the high end the value at the upper bound is about 1.3e43, as for `HyperbolicSine` at the same ``b``.
        """
        return (ParamGrid(axes=(ParamAxis("b", -1.0, 2.0, 0.02, ParamNotation.POW10),)),)

    def is_param_tuple_valid(self, b: float) -> bool:
        """Require ``b`` to be above 0."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 2.0}, x=1.0, c=0.0, expected=0.0),  # the root, at x = b/2 + c
        FormulaTestCase.value(params={"b": 2.0}, x=1.5, c=0.5, expected=0.0),
        FormulaTestCase.value(params={"b": 2.0}, x=0.0, c=0.0, expected=1.0 - math.cosh(1.0)),  # the minimum
        FormulaTestCase.value(params={"b": 2.0}, x=2.0, c=-1.0, expected=math.cosh(3.0) - math.cosh(1.0)),
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 2.0}, expected=(0.0, 2.0)),
    )
