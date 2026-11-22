"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``95–98`` in the survey of published test problems.
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


class RootsFortran20259598(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(0.04*x - 0.4)*x + 0.5 - sin(x)``; the formula's intervals are ``[0, 1]
    (95), [1, 5] (96), [5, 7] (97), [7, 10] (98)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 34)
    name = "95–98"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 95–98"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(0.04 \tmp{u} - 0.4\right) \tmp{u} + 0.5 - \sin{\left(\tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (0.04 * x - 0.4) * x + 0.5 - math.sin(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (1.0, 5.0, 4.0), (5.0, 7.0, 2.0), (7.0, 10.0, 3.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.08807979333866044),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.43012083072932167),
        FormulaTestCase.value(params={"a": 1.0, "b": 5.0, "c_scale": 4.0}, x=2.2, c=0.0, expected=-0.9948964038195901),
        FormulaTestCase.value(params={"a": 5.0, "b": 7.0, "c_scale": 2.0}, x=5.6, c=0.0, expected=0.14566663787232156),
        FormulaTestCase.value(params={"a": 7.0, "b": 10.0, "c_scale": 3.0}, x=7.9, c=0.0, expected=-1.1625413418397719),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 5.0, "c_scale": 4.0}, expected=(1.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": 5.0, "b": 7.0, "c_scale": 2.0}, expected=(5.0, 7.0)),
        FormulaTestCase.interval_bounds(params={"a": 7.0, "b": 10.0, "c_scale": 3.0}, expected=(7.0, 10.0)),
    )
