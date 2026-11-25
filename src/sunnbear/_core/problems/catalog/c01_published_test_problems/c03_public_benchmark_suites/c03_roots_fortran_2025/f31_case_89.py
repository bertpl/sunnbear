"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``89–90`` in the survey of published test problems.
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


class RootsFortran2025Case89(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``exp(1.0 - x)*(x - 1.0)*10.0 - 1.0``; the formula's intervals are ``[0,
    2] (89), [2, 5] (90)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 31)
    name = "Case 89"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 89–90"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{1 - \tmp{u}} \left(\tmp{u} - 1\right) \cdot 10 - 1",
        interval=r"[\param{a}, \param{b}]",
        summary="A function with 1 root on each of 2 adjacent intervals and its maximum between those 2 roots.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(1.0 - x) * (x - 1.0) * 10.0 - 1.0

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.0, 2.0, 1.0), (2.0, 5.0, 1.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 1.0}, x=0.6, c=0.0, expected=-6.967298790565081),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 1.0}, x=0.6, c=0.5, expected=-23.136428000412547),
        FormulaTestCase.value(params={"a": 2.0, "b": 5.0, "c_scale": 1.0}, x=2.9, c=0.0, expected=1.841803765230066),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 1.0}, expected=(0.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 5.0, "c_scale": 1.0}, expected=(2.0, 5.0)),
    )
