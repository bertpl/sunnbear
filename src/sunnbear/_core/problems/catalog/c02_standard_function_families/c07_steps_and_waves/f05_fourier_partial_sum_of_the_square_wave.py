"""This formula is the square wave's Fourier partial sum of ``n`` terms, a smooth step that overshoots and ripples."""

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


class SquareWaveFourierPartialSum(Formula):
    """`SquareWaveFourierPartialSum` is ``S_n(x - c) - d`` on ``[-1/2, 1/2]``.

    ``S_n(u) = (4/pi)*sum(k = 0 … n-1) sin((2*k + 1)*pi*u)/(2*k + 1)`` is the Fourier series of the square wave
    ``sign(sin(pi*u))`` cut off after ``n`` terms. Its slope at the root at 0 is ``4*n``; next to the jump it overshoots
    1 by about 9 % of the jump, to about 1.18, and then ripples about 1 (the Gibbs phenomenon). On ``(0, 1)`` every
    partial sum is positive.

    - ``n`` is an integer of at least 1, the number of terms. Each evaluation sums them, so its cost grows with ``n``.
    - ``d`` is the level, at least 0. At ``d = 0`` the root lies at 0, an inflection point. A larger ``d`` moves the
      root up the steep part toward the overshoot; from about 0.93 on, the level also crosses the ripples below the
      overshoot, so the interval holds several roots there.

    A pair of ``n`` and ``d`` is valid only when ``d`` lies below ``S_n(1/2)``, the value at the upper bound at
    ``c = 0``, which differs from 1 by about ``1/(pi*n)``.

    ``c`` shifts x, so the root at ``d = 0`` lies at ``x = c``.
    """

    number = (2, 7, 5)
    name = "Fourier partial sum of the square wave"
    params = (
        FormulaParam("n", latex_symbol="n", meaning="The number of terms of the Fourier series."),
        FormulaParam("d", latex_symbol="d", meaning=r"The level, between the square wave's plateaus $-1$ and 1."),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\frac{4}{\pi} \sum_{k=0}^{\param{n} - 1} \frac{\sin((2 k + 1) \pi \tmp{u})}{2 k + 1} - \param{d}",
        interval=r"\left[-\frac{1}{2}, \frac{1}{2}\right]",
        summary=(
            "A Fourier partial sum of the square wave, a smooth step that overshoots its upper plateau and ripples "
            "beside it, with 1 root in the steep part or, for a level close to 1, several next to the overshoot."
        ),
        param_conditions=(
            r"$\param{n}$ is an integer of at least 1",
            (
                r"$0 \le \param{d} < \frac{4}{\pi} \sum_{k=0}^{\param{n} - 1} \frac{(-1)^k}{2 k + 1}$, the sum at "
                r"$\x - \c = \frac{1}{2}$, so that the root lies inside the interval"
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, d: float) -> float:
        """Evaluate ``S_n(x - c) - d``."""
        pi_u = math.pi * (x - c)
        total = 0.0
        for k in range(int(n)):
            m = 2 * k + 1
            total += math.sin(m * pi_u) / m
        return (4.0 / math.pi) * total - d

    def interval_bounds(self, n: float, d: float) -> tuple[float, float]:
        """Return the interval ``[-1/2, 1/2]``."""
        return (-0.5, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one that sweeps ``n`` at ``d = 0``, and one that sweeps ``d`` at ``n = 2^10``.

        - The sweep of ``n``: from 1 to 2^12. Each evaluation sums ``n`` terms, so the sweep ends where an evaluation
          costs 2^12 sines.
        - The sweep of ``d``: from 0.01 to 0.99, at a quarter of that cost.
        """
        return (
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 12.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),
                    ParamAxis("d", 0.0, 0.0, 1.0),
                ),
                summary=(
                    r"The values of $\param{n}$ nearest to $2^{0.1 i}$, for $i$ from 0 to 120, each once, at "
                    r"$\param{d} = 0$."
                ),
            ),
            ParamGrid(
                axes=(ParamAxis("n", 10.0, 10.0, 1.0, ParamNotation.POW2), ParamAxis("d", 0.01, 0.99, 0.01)),
                summary=r"The sweep of $\param{d}$ from 0.01 to 0.99 at $\param{n} = 2^{10}$.",
            ),
        )

    def is_param_tuple_valid(self, n: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        if n >= 1.0 and n == math.floor(n) and d >= 0.0:
            value_at_half = (4.0 / math.pi) * sum((-1.0) ** k / (2 * k + 1) for k in range(int(n)))
            return d < value_at_half
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"n": 4.0, "d": 0.0}, x=0.0, c=0.0, expected=0.0),  # the root at 0
        FormulaTestCase.value(params={"n": 1.0, "d": 0.0}, x=0.5, c=0.0, expected=4.0 / math.pi),  # 1 term
        FormulaTestCase.value(
            params={"n": 2.0, "d": 0.5},
            x=0.25,
            c=0.0,
            expected=(4.0 / math.pi) * (math.sin(0.25 * math.pi) + math.sin(0.75 * math.pi) / 3.0) - 0.5,
        ),
        FormulaTestCase.value(params={"n": 4.0, "d": 0.0}, x=0.3, c=0.3, expected=0.0),  # c moves the root to x = c
        FormulaTestCase.invalid(params={"n": 0.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"n": 1.5, "d": 0.0}),
        FormulaTestCase.invalid(params={"n": 4.0, "d": -0.1}),
        FormulaTestCase.invalid(params={"n": 2.0, "d": 0.9}),  # the sum at 1/2 is (4/pi)*(2/3), about 0.85
        FormulaTestCase.interval_bounds(params={"n": 4.0, "d": 0.0}, expected=(-0.5, 0.5)),
    )
