"""This module holds a formula of Roots.jl (2026).

The formula comes from the rows with the keys ``f5`` and ``f6`` in the survey of published test problems.
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


class RootsJl2026FunctionF5(Formula):
    """This formula comes from Roots.jl (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - f5: ``x^2 - exp(x) - 3*x + 2``; the formula's interval is ``[-1.0, 1.0]``
    - f6: ``x^2 - exp(x) - 3*x + 2``; the formula's interval is ``[0.0, 3.0]``

    f5: The source's starting point is `x0 = -0.5`.

    f6: The source's starting point is `x0 = 2.0`.
    """

    number = (1, 3, 6, 7)
    name = "Function f5"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "runbenchmarks.jl, f5; runbenchmarks.jl, f6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{2} - e^{\tmp{u}} - 3 \tmp{u} + 2",
        interval=r"[\param{a}, \param{b}]",
        summary="A quadratic minus an exponential, decreasing everywhere, with 1 root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 - math.exp(x) - 3 * x + 2

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.0, 1.0, 1.0), (0.0, 3.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 1.0}, x=-0.4, c=0.0, expected=2.6896799539643608),
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 1.0}, x=-0.4, c=0.5, expected=5.103430340259401),
        FormulaTestCase.value(params={"a": 0.0, "b": 3.0, "c_scale": 1.0}, x=0.9, c=0.0, expected=-2.3496031111569495),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 1.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 3.0, "c_scale": 1.0}, expected=(0.0, 3.0)),
    )
