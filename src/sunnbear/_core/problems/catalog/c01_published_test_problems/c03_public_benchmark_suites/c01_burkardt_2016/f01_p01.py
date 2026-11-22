"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p01`` in the survey of published test problems.
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


class Burkardt2016P01(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``sin(x) - 0.5*x``; the formula's intervals are `[-1000.0, 1001.0]`
    (rang); `[0.5*pi, pi]` (starts 1 and 2).

    The values ``pi/2``, ``pi`` are rounded to 12 significant digits, the most that a parameter value holds.

    The source's starting points, in order, are `0.5*pi` and `pi`.
    """

    number = (1, 3, 1, 1)
    name = "p01"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p01"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - 0.5 \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(x) - 0.5 * x

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1000.0, 1001.0, 2000.0), (1.57079632679, 3.14159265359, 1.57)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1001.0, "c_scale": 2000.0}, x=-399.7, c=0.0, expected=200.5076786310126
        ),
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1001.0, "c_scale": 2000.0}, x=-399.7, c=0.25, expected=448.9163393621014
        ),
        FormulaTestCase.value(
            params={"a": 1.57079632679, "b": 3.14159265359, "c_scale": 1.57},
            x=2.04204,
            c=0.0,
            expected=-0.13001564370207735,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1000.0, "b": 1001.0, "c_scale": 2000.0}, expected=(-1000.0, 1001.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.57079632679, "b": 3.14159265359, "c_scale": 1.57}, expected=(1.57079632679, 3.14159265359)
        ),
    )
