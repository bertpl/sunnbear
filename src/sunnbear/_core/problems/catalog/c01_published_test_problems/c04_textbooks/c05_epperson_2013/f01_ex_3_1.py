"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``Ex. 3.1, 3.2, 3.7, 3.17; Tables 3.13, 3.17; 3.5-5; 3.9-12; 3.11-13,
3.11-14; Tables 4.13, 4.14; 4.4-1, 4.4-2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.catalog.c01_published_test_problems.shift_along_x import C_SCALE_PARAM
from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Epperson2013Ex31(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``2 - exp(x)``; the formula's intervals are `[0, 1]`; `[-5, 5]` (Fig.
    4.5).

    The chapter's running example; root `log(2) = 0.6931471806`. Bisection on `[0, 1]` (Ex. 3.1, Table 3.1); Newton from
    `x0 = 0` (Ex. 3.2, Table 3.2); secant from `x0 = 0, x1 = 1` (Ex. 3.7, Table 3.5; 3.11-13, 3.11-14); the chord method
    from `x0 = 0` (Ex. 3.17); Halley's 2 methods from `x0 = 0` (Table 3.13); Newton, Halley and Chun–Neta (Table 3.17);
    Steffensen from `x0 = 0` (3.9-12); Muller and inverse quadratic interpolation from 0, 1/2, 1 (Section 4.4).
    """

    number = (1, 4, 5, 1)
    name = "Ex. 3.1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location=(
            "Examples 3.1, 3.2, 3.7, 3.17; Tables 3.13, 3.17; Exercises 3.5-5, 3.9-12, 3.11-13, "
            "3.11-14; Tables 4.13, 4.14; Exercises 4.4-1, 4.4-2"
        ),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"2 - e^{\tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 2 - math.exp(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (-5.0, 5.0, 10.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.6501411924239969),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.948728903623976),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 5.0, "c_scale": 10.0}, x=-2.0, c=0.0, expected=1.8646647167633874
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 5.0, "c_scale": 10.0}, expected=(-5.0, 5.0)),
    )
