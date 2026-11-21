"""This module holds a formula of Ellithy (2026).

The formula comes from the rows with the keys ``17``, ``28`` and ``44`` in the survey of published test problems.
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


class Ellithy202617(Formula):
    """This formula comes from Ellithy (2026).

    The source prints 3 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 3 functions become 1 function, ``x - e*sin(x) - M``:

    - 17, with ``e = 0.8, M = 1.2``: ``x - 0.8*sin(x) - 1.2``; the formula's interval is ``[1, 3]``
    - 28, with ``e = 0.5, M = 1``: ``x - 0.5 * sin(x) - 1``; the formula's interval is ``[0, 3]``
    - 44, with ``e = 0.99, M = 2``: ``x - 0.99 * sin(x) - 2.0``; the formula's interval is ``[2.0, 3.0]``

    44: The file's note: "Kepler Equation: Eccentric anomaly for e=0.99, Mean Anomaly=2.0".
    """

    number = (1, 2, 18, 3)
    name = "17"
    params = (
        FormulaParam("e", latex_symbol="e"),
        FormulaParam("M", latex_symbol="M"),
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
        location="dataset.json, problems 17, 28 and 44",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} - \param{e} \sin{\left(\tmp{u} \right)} - \param{M}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, e: float, M: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x - e * math.sin(x) - M

    def interval_bounds(self, e: float, M: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("e", "M", "a", "b", "c_scale"),
                rows=((0.8, 1.2, 1.0, 3.0, 2.0), (0.5, 1.0, 0.0, 3.0, 3.0), (0.99, 2.0, 2.0, 3.0, 1.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"e": 0.8, "M": 1.2, "a": 1.0, "b": 3.0, "c_scale": 2.0}, x=1.6, c=0.0, expected=-0.399658882433204
        ),
        FormulaTestCase.value(
            params={"e": 0.8, "M": 1.2, "a": 1.0, "b": 3.0, "c_scale": 2.0}, x=1.6, c=0.25, expected=-0.8129658880491483
        ),
        FormulaTestCase.value(
            params={"e": 0.5, "M": 1.0, "a": 0.0, "b": 3.0, "c_scale": 3.0}, x=0.9, c=0.0, expected=-0.4916634548137417
        ),
        FormulaTestCase.value(
            params={"e": 0.99, "M": 2.0, "a": 2.0, "b": 3.0, "c_scale": 1.0},
            x=2.3,
            c=0.0,
            expected=-0.43824816005495326,
        ),
        FormulaTestCase.interval_bounds(
            params={"e": 0.8, "M": 1.2, "a": 1.0, "b": 3.0, "c_scale": 2.0}, expected=(1.0, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"e": 0.5, "M": 1.0, "a": 0.0, "b": 3.0, "c_scale": 3.0}, expected=(0.0, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"e": 0.99, "M": 2.0, "a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)
        ),
    )
