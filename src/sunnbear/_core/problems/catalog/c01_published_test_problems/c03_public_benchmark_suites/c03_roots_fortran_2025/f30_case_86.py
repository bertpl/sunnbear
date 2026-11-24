"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``86–88`` in the survey of published test problems.
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


class RootsFortran2025Case86(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``((x - 13.0)*x + 47.0)*x - 36.0 - sqrt(x)``; the formula's intervals are
    ``[0, 2] (86), [2, 6] (87), [6, 8] (88)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 30)
    name = "Case 86"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 86–88"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\left(\tmp{u} - 13.0\right) \tmp{u} + 47.0\right) \tmp{u} - 36.0 - \sqrt{\tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A cubic minus $\sqrt{\tmp{u}}$, with 1 root on each interval and an infinite slope where the function's "
            r"domain starts."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return ((x - 13.0) * x + 47.0) * x - 36.0 - math.sqrt(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 2.0, 2.0), (2.0, 6.0, 4.0), (6.0, 8.0, 2.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-13.038596669241484),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.25, expected=-31.74522776601684),
        FormulaTestCase.value(params={"a": 2.0, "b": 6.0, "c_scale": 4.0}, x=3.2, c=0.0, expected=12.259145618000167),
        FormulaTestCase.value(params={"a": 6.0, "b": 8.0, "c_scale": 2.0}, x=6.6, c=0.0, expected=-7.153046515733028),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 6.0, "c_scale": 4.0}, expected=(2.0, 6.0)),
        FormulaTestCase.interval_bounds(params={"a": 6.0, "b": 8.0, "c_scale": 2.0}, expected=(6.0, 8.0)),
    )
