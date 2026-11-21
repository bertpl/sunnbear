"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``(1.3.6)`` in the survey of published test problems.
"""

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


class Atkinson1989136(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^3 - 3*x^2 + 3*x - 1``; the formula's intervals are `[0, 2]` (Figure
    1.1); `[0.998, 1.002]` (Figure 1.2).

    Equals `(x - 1)^3`. Chapter 1 evaluates it in single precision: Figure 1.1 graphs it on `[0, 2]`, where it looks
    smooth; at 640 points of `[0.998, 1.002]` the values form a band around 0 (Figure 1.2).
    """

    number = (1, 4, 1, 2)
    name = "(1.3.6)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="Eq. (1.3.6)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3} - 3 \tmp{u}^{2} + 3 \tmp{u} - 1",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 - 3 * x**2 + 3 * x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 2.0, 2.0), (0.998, 1.002, 0.004)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-0.06400000000000002),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.25, expected=-0.7290000000000001),
        FormulaTestCase.value(
            params={"a": 0.998, "b": 1.002, "c_scale": 0.004}, x=1.0014, c=0.0, expected=2.744000000000399e-09
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.998, "b": 1.002, "c_scale": 0.004}, expected=(0.998, 1.002)),
    )
