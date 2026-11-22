"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``133`` in the survey of published test problems.
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


class RootsFortran2025133(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``y1 + ((x - x1)/(x2 - x1))*(y2 - y1)``, with the parameters ``x1 = 0.0,
    x2 = 157.08, y1 = 1012.0, y2 = -1114.0``; the formula's interval is ``[0, 157.08]``.

    the comment calls it "another linear test case" and says "see Issue #25"; `x1`, `x2`, `y1` and `y2` are constants in
    the case, and its bracket is `[x1, x2]`
    """

    number = (1, 3, 3, 37)
    name = "133"
    params = (
        FormulaParam("x1", latex_symbol="x_{1}"),
        FormulaParam("x2", latex_symbol="x_{2}"),
        FormulaParam("y1", latex_symbol="y_{1}"),
        FormulaParam("y2", latex_symbol="y_{2}"),
    )
    location_in_publication = "root_tests.f90, case 133"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 157 \c"),),
        expression=(
            r"\param{y1} + \frac{\tmp{u} - \param{x1}}{\param{x2} - \param{x1}} \left(\param{y2} - "
            r"\param{y1}\right)"
        ),
        interval="[0, 157.08]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, x1: float, x2: float, y1: float, y2: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 157.0 * c
        return y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)

    def interval_bounds(self, x1: float, x2: float, y1: float, y2: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 157.08)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("x1", "x2", "y1", "y2"),
                rows=((0.0, 157.08, 1012.0, -1114.0),),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"x1": 0.0, "x2": 157.08, "y1": 1012.0, "y2": -1114.0}, x=47.124, c=0.0, expected=374.2
        ),
        FormulaTestCase.value(
            params={"x1": 0.0, "x2": 157.08, "y1": 1012.0, "y2": -1114.0}, x=47.124, c=0.25, expected=905.4293099057804
        ),
        FormulaTestCase.interval_bounds(
            params={"x1": 0.0, "x2": 157.08, "y1": 1012.0, "y2": -1114.0}, expected=(0.0, 157.08)
        ),
    )
