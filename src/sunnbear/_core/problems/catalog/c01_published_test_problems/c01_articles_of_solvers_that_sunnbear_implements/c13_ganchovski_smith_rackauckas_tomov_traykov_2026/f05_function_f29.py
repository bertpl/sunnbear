"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f29`` in the survey of published test problems.
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


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF29(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the formula's intervals are `[2.6, 4.6]`; `[2.6,
    3.6]` (`Test Functions.pdf`).

    `Test Functions.pdf` gives the interval `[2.6, 3.6]`.
    """

    number = (1, 1, 13, 5)
    name = "Function f29"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 2, f29"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\left(\tmp{u} - 3\right)^{5}} - 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function exactly 0 in floating point on a band 0.0012 wide around its root of multiplicity 5, and "
            "increasingly steep above that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp((x - 3) ** 5) - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((2.6, 4.6, 2.0), (2.6, 3.6, 1.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0}, x=3.2, c=0.0, expected=0.0003200512054617717
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0}, x=3.2, c=0.25, expected=-0.002427049940032372
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 3.6, "c_scale": 1.0}, x=2.9, c=0.0, expected=-9.99995000016671e-06
        ),
        FormulaTestCase.interval_bounds(params={"a": 2.6, "b": 4.6, "c_scale": 2.0}, expected=(2.6, 4.6)),
        FormulaTestCase.interval_bounds(params={"a": 2.6, "b": 3.6, "c_scale": 1.0}, expected=(2.6, 3.6)),
    )
