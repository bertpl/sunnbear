"""This formula is the tangent across its poles, ``tan(0.5*pi*x - c)``, on an interval of ``2*n + 1`` sign changes."""

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


class TangentAcrossPoles(Formula):
    """`TangentAcrossPoles` is ``tan(0.5*pi*x - c)`` on ``[-(n + 1/2), n + 1/2]``.

    The scale ``0.5*pi`` puts the zeros of the tangent at the even integers and its poles at the odd integers, at
    ``c = 0``.

    ``n`` is an integer of at least 1. Each side of 0 holds the ``n`` integers 1 to ``n``, each a zero or a pole, so
    the function changes sign ``2*n + 1`` times on the interval: ``n`` or ``n + 1`` of those sign changes are poles,
    where the function has no root, and bisection can converge to one of them.

    The bounds lie halfway between a zero and a pole, where the function is -1 or 1 at ``c = 0``. For an odd ``n`` the
    function is positive at the lower bound, though it increases on every branch.

    ``c`` shifts x by ``2*c/pi``, so the roots and the poles move together.

    The function is never infinite, because no float lies exactly on a pole.

    References:
        - NIST Digital Library of Mathematical Functions, §4.14, for the definition. https://dlmf.nist.gov/4.14
    """

    number = (2, 6, 4)
    name = "Tangent across its poles"
    params = (
        FormulaParam(
            "n",
            latex_symbol="n",
            meaning=r"The number of roots and poles on each side of the root at $\x = 0$, at $\c = 0$.",
        ),
    )
    presentation = FormulaPresentation(
        expression=r"\tan\left(\frac{\pi}{2} \x - \c\right)",
        interval=r"\left[-\left(\param{n} + \frac{1}{2}\right), \param{n} + \frac{1}{2}\right]",
        summary=(
            "The tangent across its poles, whose sign changes alternate between roots and poles, where it has no root."
        ),
        param_conditions=(r"$\param{n}$ is an integer of at least 1",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``tan(0.5*pi*x - c)``."""
        return math.tan(0.5 * math.pi * x - c)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the interval ``[-(n + 1/2), n + 1/2]``."""
        return (-(n + 0.5), n + 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe of the integers ``n`` nearest to 2^0 to 2^10: every ``n`` up to 18, then fewer."""
        return (
            ParamGrid(
                axes=(ParamAxis("n", 0.0, 10.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),),
                summary=r"The values of $\param{n}$ nearest to $2^{0.1 i}$, for $i$ from 0 to 100, each once.",
            ),
        )

    def is_param_tuple_valid(self, n: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return n >= 1.0 and n == math.floor(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.0, c=0.0, expected=0.0),  # the root at 0
        FormulaTestCase.value(params={"n": 2.0}, x=2.5, c=0.0, expected=1.0),  # the upper bound
        FormulaTestCase.value(params={"n": 1.0}, x=-1.5, c=0.0, expected=1.0),  # positive at the lower bound
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=0.5 * math.pi, expected=0.0),  # c moves the root to 2*c/pi
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.3, expected=math.tan(0.25 * math.pi - 0.3)),
        FormulaTestCase.invalid(params={"n": 0.0}),
        FormulaTestCase.invalid(params={"n": 1.5}),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(-2.5, 2.5)),
    )
