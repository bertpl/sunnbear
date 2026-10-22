"""This module holds the formula of 7 in Chandrupatla (1997).

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Chandrupatla19977(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source describes ``0`` if ``abs(x) < 3.8*10^-4``, ``x*exp(-x^-2)`` otherwise; the formula's intervals are ``[-1,
    4]``; ``[-2, 5]``; ``[-1, 10]``; ``[-5, 50]``; ``[-10, 100]``.

    Printed zero: ``x = 0``. The article says Brent discusses it.
    """

    number = (1, 1, 7, 7)
    name = "7"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        if abs(x) < 3.8e-4:
            return 0.0
        else:
            return x * math.exp(-(x**-2))

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (
                        -1.0,
                        4.0,
                    ),
                    (
                        -2.0,
                        5.0,
                    ),
                    (
                        -1.0,
                        10.0,
                    ),
                    (
                        -5.0,
                        50.0,
                    ),
                    (
                        -10.0,
                        100.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"a": -2.0, "b": 5.0}, x=0.1, c=0.0, expected=3.7200759760208773e-45),
        FormulaTestCase.value(params={"a": -1.0, "b": 10.0}, x=2.3, c=0.0, expected=1.9038405842623145),
        FormulaTestCase.value(params={"a": -5.0, "b": 50.0}, x=11.5, c=0.0, expected=11.413371409313232),
        FormulaTestCase.value(params={"a": -10.0, "b": 100.0}, x=23.0, c=0.0, expected=22.956562808012574),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 5.0}, expected=(-2.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 10.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 50.0}, expected=(-5.0, 50.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 100.0}, expected=(-10.0, 100.0)),
    )
