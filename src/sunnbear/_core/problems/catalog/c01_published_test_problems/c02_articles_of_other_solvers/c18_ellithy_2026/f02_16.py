"""This module holds a formula of Ellithy (2026).

The formula comes from the rows with the keys ``16`` and ``37`` in the survey of published test problems.
"""

import math

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


class Ellithy202616(Formula):
    """This formula comes from Ellithy (2026).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``sin(k*x) - m*x``:

    - 16, with ``k = 10, m = 0.5``: ``sin(10*x) - 0.5*x``; the formula's interval is ``[0.1, 0.4]``
    - 37, with ``k = 20, m = 0.3``: ``sin(20*x) - 0.3*x``; the formula's interval is ``[0.05, 0.25]``
    """

    number = (1, 2, 18, 2)
    name = "16"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("m", latex_symbol="m"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="dataset.json, problems 16 and 37",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(\param{k} \tmp{u} \right)} - \param{m} \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, m: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(k * x) - m * x

    def interval_bounds(self, k: float, m: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("k", "m", "a", "b", "c_scale"),
                rows=((10.0, 0.5, 0.1, 0.4, 0.3), (20.0, 0.3, 0.05, 0.25, 0.2)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": 10.0, "m": 0.5, "a": 0.1, "b": 0.4, "c_scale": 0.3}, x=0.19, c=0.0, expected=0.8513000876874145
        ),
        FormulaTestCase.value(
            params={"k": 10.0, "m": 0.5, "a": 0.1, "b": 0.4, "c_scale": 0.3},
            x=0.19,
            c=0.25,
            expected=0.8552639402605211,
        ),
        FormulaTestCase.value(
            params={"k": 20.0, "m": 0.3, "a": 0.05, "b": 0.25, "c_scale": 0.2},
            x=0.11,
            c=0.0,
            expected=0.7754964038195902,
        ),
        FormulaTestCase.interval_bounds(
            params={"k": 10.0, "m": 0.5, "a": 0.1, "b": 0.4, "c_scale": 0.3}, expected=(0.1, 0.4)
        ),
        FormulaTestCase.interval_bounds(
            params={"k": 20.0, "m": 0.3, "a": 0.05, "b": 0.25, "c_scale": 0.2}, expected=(0.05, 0.25)
        ),
    )
