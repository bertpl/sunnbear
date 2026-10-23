"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``T4.7`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Gao2026T47(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-1/x^2)`` if ``x != 0``; the formula's
    intervals are ``[-1, 4]``; ``[-2, 5]``; ``[-1, 10]``; ``[-5, 50]``; ``[-10, 100]``.
    """

    number = (1, 1, 14, 5)
    name = "T4.7"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied "
            "Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        location="T4.7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        # below 1e-100, float64 rounds x*exp(-1/x^2) to 0, and x**2 underflows to 0
        if abs(x) < 1e-100:
            return 0.0
        else:
            return x * math.exp(-1 / x**2)

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(names=("a", "b"), rows=((-1.0, 4.0), (-2.0, 5.0), (-1.0, 10.0), (-5.0, 50.0), (-10.0, 100.0))),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=1e-200, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"a": -2.0, "b": 5.0}, x=0.1, c=0.0, expected=3.7200759760208773e-45, atol=0.0),
        FormulaTestCase.value(params={"a": -1.0, "b": 10.0}, x=2.3, c=0.0, expected=1.9038405842623145),
        FormulaTestCase.value(params={"a": -5.0, "b": 50.0}, x=11.5, c=0.0, expected=11.413371409313232),
        FormulaTestCase.value(params={"a": -10.0, "b": 100.0}, x=23.0, c=0.0, expected=22.956562808012574),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 5.0}, expected=(-2.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 10.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 50.0}, expected=(-5.0, 50.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 100.0}, expected=(-10.0, 100.0)),
    )
