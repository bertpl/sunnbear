"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Romadani2025Section53(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``exp(-x) - exp(-2*x) - exp(-3*x)``; the formula's intervals are `[0, 1]`
    (the bracketing methods), `[-2, 2]` (the search for the exact root) and `[-2, 60]` (the global analysis).

    Stated root `0.481211825060`. The article also states a second root near `x = 56.27` on `[-2, 60]`; the function
    equals `exp(-x)*(1 - exp(-x) - exp(-2*x))`, which has no root other than the first.
    """

    number = (1, 2, 17, 3)
    name = "Section 5.3"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section 5.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{- \tmp{u}} - e^{- 2 \tmp{u}} - e^{- 3 \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A function with 1 simple root, growing steeply in magnitude below that root, where $-e^{-3 \tmp{u}}$ "
            r"dominates, and positive but below $10^{-9}$ at more than 21 above the root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(-x) - math.exp(-2 * x) - math.exp(-3 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (-2.0, 2.0, 10.0), (-2.0, 60.0, 100.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-0.2145630751529077),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=-0.8143159699603034),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 10.0}, x=-0.8, c=0.0, expected=-13.75066787654425
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 60.0, "c_scale": 100.0}, x=16.6, c=0.0, expected=6.176060954143003e-08
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 2.0, "c_scale": 10.0}, expected=(-2.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 60.0, "c_scale": 100.0}, expected=(-2.0, 60.0)),
    )
