"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.3, §4.4; Ex. 4.1, 4.8`` in the survey of published test problems.
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
from sunnbear._core.utils.math_functions import sign


class Moler200443(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``sign(x - a)*sqrt(abs(x - a))``, with the parameters `a` free; `a = 2`
    in Figure 4.1 and Ex. 4.1; the formula's intervals are `[0, 4]` (Figure 4.1); `[1, 4]` (Ex. 4.1).

    The formula's parameter ``a_`` is the source's ``a``, renamed because ``[a, b]`` names the formula's interval.

    §4.3 derives it as the function on which Newton's method cycles forever around its zero `x = a`; the convergence
    theory for Newton's method fails on it because `f'(x)` is unbounded as `x` tends to `a`. Figure 4.1 plots it with
    `ezplot` on `[0, 4]`. §4.4 and Ex. 4.8 ask how the secant method behaves on it.
    """

    number = (1, 4, 3, 4)
    name = "§4.3"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("a", latex_symbol=r"x_{\min}"),
        FormulaParam("b", latex_symbol=r"x_{\max}"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§4.3, §4.4; Exercises 4.1, 4.8",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\operatorname{sign}{\left(\tmp{u} - \param{a_} \right)} \sqrt{\left|{\tmp{u} - " r"\param{a_}}\right|}"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return sign(x - a_) * math.sqrt(abs(x - a_))

    def interval_bounds(self, a_: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "a", "b", "c_scale"),
                rows=((2.0, 0.0, 4.0, 4.0), (2.0, 1.0, 4.0, 3.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a_": 2.0, "a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.0, expected=-0.8944271909999159
        ),
        FormulaTestCase.value(
            params={"a_": 2.0, "a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.25, expected=-1.3416407864998738
        ),
        FormulaTestCase.value(
            params={"a_": 2.0, "a": 1.0, "b": 4.0, "c_scale": 3.0}, x=1.9, c=0.0, expected=-0.31622776601683805
        ),
        FormulaTestCase.interval_bounds(params={"a_": 2.0, "a": 0.0, "b": 4.0, "c_scale": 4.0}, expected=(0.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a_": 2.0, "a": 1.0, "b": 4.0, "c_scale": 3.0}, expected=(1.0, 4.0)),
    )
