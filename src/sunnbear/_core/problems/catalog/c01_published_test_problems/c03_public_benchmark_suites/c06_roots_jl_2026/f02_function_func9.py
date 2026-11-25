"""This module holds a formula of Roots.jl (2026).

The formula comes from the rows with the keys ``func9`` and ``f7`` in the survey of published test problems.
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


class RootsJl2026FunctionFunc9(Formula):
    """This formula comes from Roots.jl (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - func9: ``tanh(x) - tan(x)``; the formula's interval is `[5, 12]` (`find_zeros`)
    - f7: ``tanh(x) - tan(x)``; the formula's interval is ``[4.0, 8.0]``

    func9: The source's 8 starting points are evenly spaced from `5.0` to `10.0`.

    f7: The source's starting point is `x0 = 7.6`.
    """

    number = (1, 3, 6, 2)
    name = "Function func9"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "test_derivative_free.jl, func9; runbenchmarks.jl, f7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tanh{\left(\tmp{u} \right)} - \tan{\left(\tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A hyperbolic tangent minus a tangent, with 2 roots and 2 poles on the wide interval, and 1 root and 2 "
            "poles on the narrow one."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.tanh(x) - math.tan(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((5.0, 12.0, 10.0), (4.0, 8.0, 10.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 5.0, "b": 12.0, "c_scale": 10.0}, x=7.1, c=0.0, expected=-0.06489448847872395
        ),
        FormulaTestCase.value(
            params={"a": 5.0, "b": 12.0, "c_scale": 10.0}, x=7.1, c=0.175, expected=2.349779305773395
        ),
        FormulaTestCase.value(params={"a": 4.0, "b": 8.0, "c_scale": 10.0}, x=5.2, c=0.0, expected=2.885581014405963),
        FormulaTestCase.interval_bounds(params={"a": 5.0, "b": 12.0, "c_scale": 10.0}, expected=(5.0, 12.0)),
        FormulaTestCase.interval_bounds(params={"a": 4.0, "b": 8.0, "c_scale": 10.0}, expected=(4.0, 8.0)),
    )
