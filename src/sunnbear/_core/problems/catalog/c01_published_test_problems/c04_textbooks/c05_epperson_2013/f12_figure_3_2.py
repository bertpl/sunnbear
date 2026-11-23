"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``Fig. 3.2, 3.6, 3.7`` in the survey of published test problems.
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


class Epperson2013Figure32(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^2 - 1/2``; the formula's intervals are `[0, 4]` (Fig. 3.2, 3.6); `[0,
    2]` (Fig. 3.7).

    Roots `±sqrt(1/2)`. Figures only: Newton's tangent lines (Fig. 3.2), secant lines (Fig. 3.6), and its fixed point
    `(1 + sqrt(3))/2` next to its root (Fig. 3.7).
    """

    number = (1, 4, 5, 12)
    name = "Figure 3.2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Fig. 3.2, 3.6, 3.7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{2} - \frac{1}{2}",
        interval=r"[\param{a}, \param{b}]",
        summary="A parabola with its vertex at the lower bound of both intervals and 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 - 1 / 2

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.0, 4.0, 4.0), (0.0, 2.0, 2.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.0, expected=0.94),
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.25, expected=-0.46),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-0.14),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, expected=(0.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
    )
