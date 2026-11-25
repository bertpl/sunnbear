"""This formula is the sine with its zeros at the even integers, ``sin(0.5*pi*x - c)``."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
    ParamRounding,
)


class Sine(Formula):
    """`Sine` is ``sin(0.5*pi*x - c)`` on ``[-b, b]``.

    The scale ``0.5*pi`` puts the zeros of the sine at the even integers and its extrema at the odd integers, at
    ``c = 0``. Every root is an inflection point.

    ``b`` is the upper bound of the interval, any value above 0:

    - below 1, the function is monotone on the interval, and close to a line for a small ``b``;
    - below 2, the interval holds 1 root, and from ``b = 1`` on it also holds both extrema next to that root;
    - at an odd ``b``, both bounds lie on extrema, and the interval holds ``b`` roots.

    ``c`` shifts x by ``2*c/pi``, so the root at 0 moves to ``x = 2*c/pi``, and every other root with it.

    References:
        - NIST Digital Library of Mathematical Functions, §4.14, for the definition. https://dlmf.nist.gov/4.14
    """

    number = (2, 6, 1)
    name = "Sine"
    params = (FormulaParam("b", latex_symbol="b"),)
    presentation = FormulaPresentation(
        expression=r"\sin\left(\frac{\pi}{2} \x - \c\right)",
        interval=r"[-\param{b}, \param{b}]",
        summary="The sine, from nearly a line on a narrow interval to many roots at equal distances on a wide one.",
        param_conditions=(r"$\param{b} > 0$",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``sin(0.5*pi*x - c)``."""
        return math.sin(0.5 * math.pi * x - c)

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: a sweep of a small ``b``, and the odd values of a large ``b``.

        - The sweep of a small ``b``: from 2^-10 to 2^0.9. The interval holds 1 root throughout, because the next zeros,
          at -2 and 2, stay outside; from ``b = 1`` on, it also holds both extrema next to that root.
        - The odd values of a large ``b``: the odd integers nearest to 2^0.1 to 2^10, which put both bounds on extrema.
          The values of ``c`` that keep the sign of the function at both bounds then reach their widest range,
          about ±1.47.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("b", -10.0, 0.9, 0.1, ParamNotation.POW2),),
                summary=r"The sweep of $\param{b}$ from $2^{-10}$ to $2^{0.9}$.",
            ),
            ParamGrid(
                axes=(ParamAxis("b", 0.1, 10.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_ODD_INTEGER),),
                summary=r"The odd values of $\param{b}$ nearest to $2^{0.1 i}$, for $i$ from 1 to 100, each once.",
            ),
        )

    def is_param_tuple_valid(self, b: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 3.0}, x=0.0, c=0.0, expected=0.0),  # the root at 0
        FormulaTestCase.value(params={"b": 3.0}, x=1.0, c=0.0, expected=1.0),  # a maximum
        FormulaTestCase.value(params={"b": 3.0}, x=-3.0, c=0.0, expected=1.0),  # the lower bound, on a maximum
        FormulaTestCase.value(params={"b": 3.0}, x=1.0, c=0.5 * math.pi, expected=0.0),  # c moves the root to 2*c/pi
        FormulaTestCase.value(params={"b": 0.5}, x=0.5, c=0.25, expected=math.sin(0.25 * math.pi - 0.25)),
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 3.0}, expected=(-3.0, 3.0)),
    )
