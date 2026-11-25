"""This module holds a formula of Roots.jl (2026).

The formula comes from the rows with the keys ``func2`` and ``f3`` in the survey of published test problems.
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


class RootsJl2026FunctionFunc2(Formula):
    """This formula comes from Roots.jl (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - func2: ``exp(x) - x^4``; the formula's interval is `[-5.0, 20.0]` (`find_zeros`)
    - f3: ``exp(x) - x^4``; the formula's interval is ``[5.0, 20.0]``

    func2: The source's 11 starting points are evenly spaced from `5.0` to `20.0`.

    f3: The source's starting point is `x0 = 7.0`.
    """

    number = (1, 3, 6, 1)
    name = "Function func2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "test_derivative_free.jl, func2; runbenchmarks.jl, f3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}} - \tmp{u}^{4}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "An exponential minus a quartic, with 3 roots on the wide interval and 1 on the narrow one, rising steeply "
            "above the highest root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - x**4

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-5.0, 20.0, 10.0), (5.0, 20.0, 10.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -5.0, "b": 20.0, "c_scale": 10.0}, x=2.5, c=0.0, expected=-26.880006039296525
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 20.0, "c_scale": 10.0}, x=2.5, c=0.625, expected=-197.730388504144
        ),
        FormulaTestCase.value(params={"a": 5.0, "b": 20.0, "c_scale": 10.0}, x=9.5, c=0.0, expected=5214.664329661872),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 20.0, "c_scale": 10.0}, expected=(-5.0, 20.0)),
        FormulaTestCase.interval_bounds(params={"a": 5.0, "b": 20.0, "c_scale": 10.0}, expected=(5.0, 20.0)),
    )
