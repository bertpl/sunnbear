"""This formula is the exponential function minus 1, shifted by ``c`` along x, ``exp(x - c) - 1``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamNotation, ParamRecipe


class Exponential(Formula):
    """`Exponential` is ``exp(x - c) - 1`` on ``[-b, b]``.

    ``b`` is the upper bound of the interval, any value above 0.

    The function is close to the line ``x - c`` for a small ``b``. For a large ``b``, it is close to -1 over most of
    the lower half of the interval, and grows as an exponential toward the upper bound.

    ``c`` shifts x, so the root lies at ``x = c``. Next to the root, ``exp(x - c)`` is close to 1, so the function is
    computed as ``expm1(x - c)``, which keeps its full precision there.

    References:
        - NIST Digital Library of Mathematical Functions, §4.2, for the definition. https://dlmf.nist.gov/4.2
    """

    number = (2, 5, 1)
    name = "Exponential"
    param_names = ("b",)

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``exp(x - c) - 1`` as ``expm1(x - c)``."""
        return math.expm1(x - c)

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^-1 to 10^2.

        At the low end the function is close to a line. At the high end its value at the upper bound is about 2.7e43.
        """
        return (ParamGrid(axes=(ParamAxis("b", -1.0, 2.0, 0.02, ParamNotation.POW10),)),)

    def is_param_tuple_valid(self, b: float) -> bool:
        """Require ``b`` to be above 0."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 1.0}, x=0.0, c=0.0, expected=0.0),  # the root, at x = c
        FormulaTestCase.value(params={"b": 1.0}, x=0.5, c=0.5, expected=0.0),
        FormulaTestCase.value(params={"b": 10.0}, x=10.0, c=0.0, expected=math.exp(10.0) - 1.0),
        FormulaTestCase.value(params={"b": 10.0}, x=-10.0, c=1.0, expected=math.exp(-11.0) - 1.0),  # c shifts x
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 10.0}, expected=(-10.0, 10.0)),
    )
