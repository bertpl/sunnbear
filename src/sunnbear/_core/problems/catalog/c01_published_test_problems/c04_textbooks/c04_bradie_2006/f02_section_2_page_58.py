"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``§2 (p. 58)`` in the survey of published test problems.
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


class Bradie2006Section2Page58(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``3*x^2 + (1/pi^4)*log((pi - x)^2) + 1``; the formula's intervals are
    `(pi - 1, pi)`; `(pi, pi + 1)`.

    The values ``-1 + pi``, ``pi``, ``1 + pi`` are rounded to 12 significant digits, the most that a parameter value
    holds.

    Undefined at `x = pi`. 2 simple real roots, 1 in `(pi - 1, pi)` and 1 in `(pi, pi + 1)`, both at about `pi ±
    10^-647`, which no floating-point system resolves: the book's pathological example.
    """

    number = (1, 4, 4, 2)
    name = "Section 2 (page 58)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§2 (p. 58)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"3 \tmp{u}^{2} + \frac{\ln{\left(\left(\pi - \tmp{u}\right)^{2} \right)}}{\pi^{4}} + 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A function with 2 roots within $10^{-647}$ of $\x = \pi$ on the lower interval, positive at every float "
            r"except the one nearest $\pi$, where the evaluation gives $-\infty$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 3 * x**2 + (1 / math.pi**4) * math.log((math.pi - x) ** 2) + 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((2.14159265359, 3.14159265359, 1.0), (3.14159265359, 4.14159265359, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 2.14159265359, "b": 3.14159265359, "c_scale": 1.0},
            x=2.44159,
            c=0.0,
            expected=18.876762024842968,
        ),
        FormulaTestCase.value(
            params={"a": 2.14159265359, "b": 3.14159265359, "c_scale": 1.0},
            x=2.44159,
            c=0.25,
            expected=15.408147089550948,
        ),
        FormulaTestCase.value(
            params={"a": 3.14159265359, "b": 4.14159265359, "c_scale": 1.0},
            x=3.44159,
            c=0.0,
            expected=36.50890507579916,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.14159265359, "b": 3.14159265359, "c_scale": 1.0}, expected=(2.14159265359, 3.14159265359)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 3.14159265359, "b": 4.14159265359, "c_scale": 1.0}, expected=(3.14159265359, 4.14159265359)
        ),
    )
