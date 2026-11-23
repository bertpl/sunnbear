"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.4`` in the survey of published test problems.
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


class Romadani2025Section54(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``cos(exp(x/2))^3 - x^3``; the formula's intervals are `[0, 1]` (the
    bracketing methods) and `[-1, 1]` (the search for the exact root).

    Printed as `cos^3(e^(x/2)) - x^3`. Stated root `0.363177127637`.
    """

    number = (1, 2, 17, 4)
    name = "Section 5.4"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section 5.4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\cos^{3}{\left(e^{\frac{\tmp{u}}{2}} \right)} - \tmp{u}^{3}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A decreasing function, more than 8 times steeper at $\x = \pm 1$ than near $\x = 0$, with 1 simple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.cos(math.exp(x / 2)) ** 3 - x**3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (-1.0, 1.0, 2.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.03588203867309906),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.13953564474479144),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.0, expected=0.38282008000056855
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
    )
