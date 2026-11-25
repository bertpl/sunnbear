"""This module holds formula f1.99.1.7.9, the modified version of the published formula f1.1.7.9.

A change of formula f1.1.7.9 may need a matching change of this module.
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


class ModifiedChandrupatla1997Function9(Formula):
    """This formula is the modified version of formula f1.1.7.9, from Chandrupatla (1997).

    The survey writes the source's function as ``exp(x) - 2 - 0.01/x^2 + 0.000002/x^3``; the published intervals are
    `[2E-4, 1]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`; `[2E-4, 81]`.

    Printed zero: `x = 0.7032`.

    The formula holds the test problems on ``[2e-4, 9]`` and wider. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on the published interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c``
    and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problems on ``[2e-4, 9]`` and wider do not satisfy the benchmark suite inclusion conditions,
    because each interval spans orders of magnitude next to the pole at 0, so that the shift by ``c_scale*c`` at the
    smallest ``c`` that the benchmark suite pipeline tries changes the sign of ``f(a)``.
    """

    number = (1, 99, 1, 7, 9)
    name = "Function 9"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
    )
    location_in_publication = "Table 1, function 9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x e^{-\c \ln(\param{b}/\param{a})}"),),
        expression=r"e^{\tmp{u}} - 2 - \frac{0.01}{\tmp{u}^{2}} + \frac{2 \cdot 10^{-6}}{\tmp{u}^{3}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A function with a simple root and, below that root, a narrow dip to about $-3.7 \cdot 10^{4}$, a second "
            r"root, and a pole of order 3 at $\x = 0$."
        ),
        notes=(
            (
                r"$\c$ scales x, so that the root moves by the factor $(\param{b}/\param{a})^{\c}$ and "
                "never reaches 0: the interval spans orders of magnitude next to the pole at 0, and a "
                "shift along x would move the lower bound across it."
            ),
        ),
    )
    effect_of_c = EffectOfC.SCALES_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``."""
        x = x * math.exp(-c * math.log(b / a))
        return math.exp(x) - 2 - 0.01 / x**2 + 0.000002 / x**3

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (0.0002, 9.0),
                    (0.0002, 27.0),
                    (0.0002, 81.0),
                ),
                summary="The published intervals $[2 \\cdot 10^{-4}, 9]$ and wider.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0002, "b": 9.0}, x=0.123868, c=0.25, expected=-135.99740114601173),
        FormulaTestCase.value(params={"a": 0.0002, "b": 27.0}, x=0.239458, c=0.25, expected=-64.03944642544192),
        FormulaTestCase.value(params={"a": 0.0002, "b": 81.0}, x=0.462917, c=0.25, expected=-30.355396483422293),
    )
