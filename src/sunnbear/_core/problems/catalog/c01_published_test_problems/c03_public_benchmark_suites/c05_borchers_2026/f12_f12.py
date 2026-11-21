"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f12`` in the survey of published test problems.
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


class Borchers2026F12(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``log(x) + x^2/(2*exp(1)) - 2*x/sqrt(exp(1)) + 1``; the formula's
    intervals are `[1, 3.4]`; `[1.0, 2.5]` (figure of §5.2.3).

    Printed root: `1.64872127070`; §5.2.3 calls it extremely flat around the root, compares 7 solvers at `tol = 1e-15`
    (`fzero` from starting point 2.2), and solves it with `ridders` on [1, 3.4] in 128-bit precision, as `f12a` with
    `exp(m1)` for `exp(1)`, `m1 = Rmpfr::mpfr(1.0, 128)`; it gives the true root as `sqrt(exp(1))`
    """

    number = (1, 3, 5, 12)
    name = "f12"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        C_SCALE_PARAM,
    )
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="§5.6, f12",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\ln{\left(\tmp{u} \right)} + \frac{\tmp{u}^{2}}{2 e^{1}} - \frac{2 \tmp{u}}{\sqrt{e^{1}}} " r"+ 1"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.log(x) + x**2 / (2 * math.exp(1)) - 2 * x / math.sqrt(math.exp(1)) + 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((1.0, 3.4, 2.4), (1.0, 2.5, 1.5)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4}, x=1.72, c=0.0, expected=2.609079470017915e-05
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4}, x=1.72, c=0.25, expected=-0.01456600694656706
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 2.5, "c_scale": 1.5}, x=1.45, c=0.0, expected=-0.0006420942026751546
        ),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 3.4, "c_scale": 2.4}, expected=(1.0, 3.4)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 2.5, "c_scale": 1.5}, expected=(1.0, 2.5)),
    )
