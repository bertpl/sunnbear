"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p06`` in the survey of published test problems.
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


class Burkardt2016ProblemP06(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 2.0 - 1.0/(10.0*x)^2 + 2.0/(100.0*x)^3``; the formula's
    intervals are `[0.00001, 20.0]` (rang); `[0.0002, 2.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.0002` and `2.0`. The title has `- 2 / ( 100 * X )^3` where the code
    and the docstring have `+`. The function does not change sign on `rang`, `[0.00001, 20.0]`, which holds 2 roots,
    about `0.0001999992` and `0.7032048404`; `p06_root` returns only the 2nd, `0.7032048403631358`.
    """

    number = (1, 3, 1, 6)
    name = "Problem p06"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p06"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"e^{\tmp{u}} - 2.0 - \frac{1.0}{\left(10.0 \tmp{u}\right)^{2}} + \frac{2.0}{\left(100.0 "
            r"\tmp{u}\right)^{3}}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A function with 2 roots on the wide interval, so that it has the same sign at both bounds of that "
            r"interval, and 1 on the narrow one, which starts $8 \cdot 10^{-10}$ above the lower root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - 2.0 - 1.0 / (10.0 * x) ** 2 + 2.0 / (100.0 * x) ** 3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((1e-05, 20.0, 20.0), (0.0002, 2.0, 2.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.0, expected=401.4325500332488
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.25, expected=0.7083112113502446
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 2.0, "c_scale": 2.0}, x=0.60014, c=0.0, expected=-0.2053816516894782
        ),
        FormulaTestCase.interval_bounds(params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, expected=(1e-05, 20.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0002, "b": 2.0, "c_scale": 2.0}, expected=(0.0002, 2.0)),
    )
