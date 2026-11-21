"""This module holds a formula of Ridders (1979).

The formula comes from the row with the key ``III.2`` in the survey of published test problems.
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


class Ridders1979Iii2(Formula):
    """This formula comes from Ridders (1979).

    The survey writes the source's function as ``tan(x)^tan(x) - 10^3``; the formula's intervals are `[1.3, 1.4]`; `[0,
    1.5]`.

    Last printed iterate: `1.354710442`.
    """

    number = (1, 1, 5, 3)
    name = "III.2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous"
            " function. IEEE Transactions on Circuits and Systems 26(11), 979–980. "
            "https://doi.org/10.1109/TCS.1979.1084580."
        ),
        location="Section III, function 2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tan^{\tan{\left(\tmp{u} \right)}}{\left(\tmp{u} \right)} - 10^{3}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.tan(x) ** math.tan(x) - 10**3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((1.3, 1.4, 0.1), (0.0, 1.5, 1.5)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 1.3, "b": 1.4, "c_scale": 0.1}, x=1.33, c=0.0, expected=-695.5887196520625),
        FormulaTestCase.value(params={"a": 1.3, "b": 1.4, "c_scale": 0.1}, x=1.33, c=0.25, expected=-880.9903886606878),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.5, "c_scale": 1.5}, x=0.45, c=0.0, expected=-999.2963560197811),
        FormulaTestCase.interval_bounds(params={"a": 1.3, "b": 1.4, "c_scale": 0.1}, expected=(1.3, 1.4)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.5, "c_scale": 1.5}, expected=(0.0, 1.5)),
    )
