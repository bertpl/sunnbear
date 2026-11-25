"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p05`` in the survey of published test problems.
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


class Burkardt2016ProblemP05(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``(x + 3.0)*(x - 1.0)*(x - 1.0)``; the formula's intervals are `[-1000.0,
    1000.0]` (rang); `[-5.0, 2.0]` (starts 2 and 1).

    The source's starting points, in order, are `2.0` and `-5.0`.
    """

    number = (1, 3, 1, 5)
    name = "Problem p05"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p05"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} + 3\right) \left(\tmp{u} - 1\right) \left(\tmp{u} - 1\right)",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A cubic with a simple root on the interval and, 4 above that root, a double root, where the cubic touches "
            "0 without changing sign."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 3.0) * (x - 1.0) * (x - 1.0)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1000.0, 1000.0, 2000.0), (-5.0, 2.0, 7.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, x=-400.0, c=0.0, expected=-63837997.0
        ),
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, x=-400.0, c=0.25, expected=-728185497.0
        ),
        FormulaTestCase.value(params={"a": -5.0, "b": 2.0, "c_scale": 7.0}, x=-2.9, c=0.0, expected=1.5210000000000012),
        FormulaTestCase.interval_bounds(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, expected=(-1000.0, 1000.0)
        ),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 2.0, "c_scale": 7.0}, expected=(-5.0, 2.0)),
    )
