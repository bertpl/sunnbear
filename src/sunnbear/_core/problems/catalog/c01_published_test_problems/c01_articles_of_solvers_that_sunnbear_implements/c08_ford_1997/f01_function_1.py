"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``1`` in the survey of published test problems.
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


class Ford1997Function1(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``sin(0.01/x) - 0.01``; the formula's intervals are `[0.5, 2]`; `[0.2,
    6]`; `[0.004, 200]`.

    Printed root: `x* = 0.99998333286109`.
    """

    number = (1, 1, 8, 1)
    name = "Function 1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section “Numerical Tests”, function 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(\frac{0.01}{\tmp{u}} \right)} - 0.01",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A function with 1 root, where the slope is about $-0.01$; the maximum nearest that root is 0.99, at $\x ="
            r" 0.02/\pi + \param{c_scale} \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(0.01 / x) - 0.01

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.5, 2.0, 1.5), (0.2, 6.0, 5.8), (0.004, 200.0, 200.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.5, "b": 2.0, "c_scale": 1.5}, x=0.95, c=0.0, expected=0.0005261213987539786
        ),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 2.0, "c_scale": 1.5}, x=0.95, c=0.25, expected=0.00739042767277413
        ),
        FormulaTestCase.value(
            params={"a": 0.2, "b": 6.0, "c_scale": 5.8}, x=1.94, c=0.0, expected=-0.004845383651434474
        ),
        FormulaTestCase.value(
            params={"a": 0.004, "b": 200.0, "c_scale": 200.0}, x=60.0028, c=0.0, expected=-0.009833341111519662
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.5, "b": 2.0, "c_scale": 1.5}, expected=(0.5, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.2, "b": 6.0, "c_scale": 5.8}, expected=(0.2, 6.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.004, "b": 200.0, "c_scale": 200.0}, expected=(0.004, 200.0)),
    )
