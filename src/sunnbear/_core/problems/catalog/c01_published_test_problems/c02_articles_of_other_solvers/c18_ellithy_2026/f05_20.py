"""This module holds a formula of Ellithy (2026).

The formula comes from the rows with the keys ``20`` and ``39`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.catalog.c01_published_test_problems.shift_along_x import C_SCALE_PARAM
from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Ellithy202620(Formula):
    """This formula comes from Ellithy (2026).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``exp(x^2) - exp(k*x)``:

    - 20, with ``k = 2^(1/2)``: ``exp(x^2) - exp(sqrt(2)*x)``; the formula's interval is ``[0.5, 1.5]``
    - 39, with ``k = 1.2``: ``exp(x^2) - exp(1.2*x)``; the formula's interval is ``[0, 2]``
    """

    number = (1, 2, 18, 5)
    name = "20"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="dataset.json, problems 20 and 39",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}^{2}} - e^{\param{k} \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x**2) - math.exp(k * x)

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("k", "a", "b", "c_scale"),
                rows=((1.4142135623730951, 0.5, 1.5, 1.0), (1.2, 0.0, 2.0, 2.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": 1.4142135623730951, "a": 0.5, "b": 1.5, "c_scale": 1.0},
            x=0.8,
            c=0.0,
            expected=-1.203422211272692,
        ),
        FormulaTestCase.value(
            params={"k": 1.4142135623730951, "a": 0.5, "b": 1.5, "c_scale": 1.0},
            x=0.8,
            c=0.25,
            expected=-0.8234786290091135,
        ),
        FormulaTestCase.value(
            params={"k": 1.2, "a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-0.6211037960835475
        ),
        FormulaTestCase.interval_bounds(
            params={"k": 1.4142135623730951, "a": 0.5, "b": 1.5, "c_scale": 1.0}, expected=(0.5, 1.5)
        ),
        FormulaTestCase.interval_bounds(params={"k": 1.2, "a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
    )
