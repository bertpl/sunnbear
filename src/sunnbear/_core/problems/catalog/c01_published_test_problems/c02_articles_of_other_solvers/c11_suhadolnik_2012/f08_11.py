"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``11`` in the survey of published test problems.
"""

import math

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


class Suhadolnik201211(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``atan(x) - 1``; the formula's intervals are `[1, 8]`; `[0, 9]` (Fig. 1,
    2).

    The article prints `arctan`.
    """

    number = (1, 2, 11, 8)
    name = "11"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="Table 1, function 11",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\arctan{\left(\tmp{u} \right)} - 1",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.atan(x) - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((1.0, 8.0, 7.0), (0.0, 9.0, 9.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 1.0, "b": 8.0, "c_scale": 7.0}, x=3.1, c=0.0, expected=0.2587542052323633),
        FormulaTestCase.value(params={"a": 1.0, "b": 8.0, "c_scale": 7.0}, x=3.1, c=0.25, expected=-0.0667524713437961),
        FormulaTestCase.value(params={"a": 0.0, "b": 9.0, "c_scale": 9.0}, x=2.7, c=0.0, expected=0.21609067478395633),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 8.0, "c_scale": 7.0}, expected=(1.0, 8.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 9.0, "c_scale": 9.0}, expected=(0.0, 9.0)),
    )
