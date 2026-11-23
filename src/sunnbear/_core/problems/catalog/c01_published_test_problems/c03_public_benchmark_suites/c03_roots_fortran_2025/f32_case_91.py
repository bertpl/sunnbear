"""This module holds a formula of roots-fortran (2025).

The formula comes from the rows with the keys ``91`` and ``92`` in the survey of published test problems.
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


class RootsFortran2025Case91(Formula):
    """This formula comes from roots-fortran (2025).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``exp(x) + x - k``:

    - 91, with ``k = 20.0``: ``exp(x) + x - 20.0``; the formula's interval is ``[2, 3]``
    - 92, with ``k = 5.0``: ``exp(x) + x - 5.0``; the formula's interval is ``[0, 2]``

    92: the comment says the root in the paper is wrong for this case
    """

    number = (1, 3, 3, 32)
    name = "Case 91"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 91 and 92"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}} + \tmp{u} - \param{k}",
        interval=r"[\param{a}, \param{b}]",
        summary="An increasing, convex function with 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) + x - k

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("k", "a", "b", "c_scale"),
                rows=((20.0, 2.0, 3.0, 1.0), (5.0, 0.0, 2.0, 2.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": 20.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.0, expected=-7.725817545185281
        ),
        FormulaTestCase.value(
            params={"k": 20.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.25, expected=-10.18209889369323
        ),
        FormulaTestCase.value(
            params={"k": 5.0, "a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-2.5778811996094912
        ),
        FormulaTestCase.interval_bounds(params={"k": 20.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"k": 5.0, "a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
    )
