"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f6`` in the survey of published test problems.
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


class Borchers2026F6(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``(x - 1)*exp(-9*x) + x^9``; the formula's intervals are ``[-0.8, 1.6],
    [-1.4, 1.0]``.

    Printed root: `0.5367416626`; section 5.6 gives [-0.8, 1.6]; §5.1.1 solves it on [-1.4, 1.0] with `brentDekker`, and
    §5.1.2 with `ridders`
    """

    number = (1, 3, 5, 6)
    name = "f6"
    params = (
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
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="§5.6, f6",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} - 1\right) e^{- 9 \tmp{u}} + \tmp{u}^{9}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x - 1) * math.exp(-9 * x) + x**9

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-0.8, 1.6, 2.4), (-1.4, 1.0, 2.4)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -0.8, "b": 1.6, "c_scale": 2.4}, x=-0.08, c=0.0, expected=-2.2187878676296164
        ),
        FormulaTestCase.value(
            params={"a": -0.8, "b": 1.6, "c_scale": 2.4}, x=-0.08, c=0.25, expected=-764.2037738594979
        ),
        FormulaTestCase.value(
            params={"a": -1.4, "b": 1.0, "c_scale": 2.4}, x=-0.68, c=0.0, expected=-764.2037738594987
        ),
        FormulaTestCase.interval_bounds(params={"a": -0.8, "b": 1.6, "c_scale": 2.4}, expected=(-0.8, 1.6)),
        FormulaTestCase.interval_bounds(params={"a": -1.4, "b": 1.0, "c_scale": 2.4}, expected=(-1.4, 1.0)),
    )
