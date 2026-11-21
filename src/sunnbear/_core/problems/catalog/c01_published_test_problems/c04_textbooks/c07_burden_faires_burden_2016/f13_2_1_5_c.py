"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the rows with the keys ``2.1-5(c)`` and ``2.3-6(c)`` in the survey of published test problems.
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


class BurdenFairesBurden2016215C(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``2*x*cos(2*x) - (x - k)^2``:

    - 2.1-5(c), with ``k = -1``: ``2*x*cos(2*x) - (x + 1)^2``; the formula's intervals are `[-3, -2]`; `[-1, 0]`
    - 2.3-6(c), with ``k = 2``: ``2*x*cos(2*x) - (x - 2)^2``; the formula's intervals are `[2, 3]`; `[3, 4]`

    2.1-5(c): As 2.1-5(b).

    2.3-6(c): As 2.3-6(a).
    """

    number = (1, 4, 7, 13)
    name = "2.1-5(c)"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercises 2.1-5(c), 2.3-6(c)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"2 \tmp{u} \cos{\left(2 \tmp{u} \right)} - \left(\tmp{u} - \param{k}\right)^{2}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 2 * x * math.cos(2 * x) - (x - k) ** 2

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("k", "a", "b", "c_scale"),
                rows=((-1.0, -3.0, -2.0, 1.0), (-1.0, -1.0, 0.0, 1.0), (2.0, 2.0, 3.0, 1.0), (2.0, 3.0, 4.0, 1.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": -1.0, "a": -3.0, "b": -2.0, "c_scale": 1.0}, x=-2.7, c=0.0, expected=-6.317341530090228
        ),
        FormulaTestCase.value(
            params={"k": -1.0, "a": -3.0, "b": -2.0, "c_scale": 1.0}, x=-2.7, c=0.25, expected=-9.274622741389813
        ),
        FormulaTestCase.value(
            params={"k": -1.0, "a": -1.0, "b": 0.0, "c_scale": 1.0}, x=-0.7, c=0.0, expected=-0.3279540000603374
        ),
        FormulaTestCase.value(
            params={"k": 2.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.0, expected=-0.6059016239012522
        ),
        FormulaTestCase.value(
            params={"k": 2.0, "a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=4.581535106926295
        ),
        FormulaTestCase.interval_bounds(
            params={"k": -1.0, "a": -3.0, "b": -2.0, "c_scale": 1.0}, expected=(-3.0, -2.0)
        ),
        FormulaTestCase.interval_bounds(params={"k": -1.0, "a": -1.0, "b": 0.0, "c_scale": 1.0}, expected=(-1.0, 0.0)),
        FormulaTestCase.interval_bounds(params={"k": 2.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"k": 2.0, "a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
    )
