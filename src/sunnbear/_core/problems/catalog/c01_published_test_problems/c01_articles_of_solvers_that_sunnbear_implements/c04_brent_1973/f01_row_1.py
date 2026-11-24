"""This module holds a formula of Brent (1973).

The formula comes from the row with the key ``T4.1 r1-2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Brent1973Row1(Formula):
    """This formula comes from Brent (1973).

    The survey writes the source's function as ``x^9``; the formula's intervals are `[-1.0, +1.1]` with the absolute
    tolerance `t = 1E-9` of procedure `zero2`; `[-1.0, +4.0]` with `t = 1E-20`.

    Section 2 (p. 48) also names `x^9`: on an IBM 360, `f` vanished on an interval through underflow, and Dekker's
    procedure then took many small steps.
    """

    number = (1, 1, 4, 1)
    name = "Row 1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 4.1, rows 1 and 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{9}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A 9th power, flat at its root of multiplicity 9 and below $10^{-4}$ in magnitude within 0.35 of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**9

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.0, 1.1, 2.1), (-1.0, 4.0, 5.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.1, "c_scale": 2.1}, x=-0.37, c=0.0, expected=-0.00012996173979507698
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.1, "c_scale": 2.1}, x=-0.37, c=0.25, expected=-0.36847439787320274
        ),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.0, expected=0.001953125),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.1, "c_scale": 2.1}, expected=(-1.0, 1.1)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, expected=(-1.0, 4.0)),
    )
