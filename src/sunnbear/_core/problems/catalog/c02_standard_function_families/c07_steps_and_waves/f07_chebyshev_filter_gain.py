"""This formula is the gain of the Chebyshev filter of order ``n``, which ripples and then falls in a steep step."""

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


class ChebyshevFilterGain(Formula):
    """`ChebyshevFilterGain` is ``G_n(x - c) - d`` on ``[0, 2]``, with the gain ``G_n(u) = 1/sqrt(1 + T_n(abs(u))^2)``.

    ``G_n`` is the gain of the Chebyshev low-pass filter of type I, of order ``n`` and with the ripple factor 1, at the
    frequency ``u`` relative to its cutoff; the filter of type II is usually called the inverse Chebyshev filter.
    ``T_n`` is the Chebyshev polynomial of the 1st kind, which is ``cos(n*acos(u))`` on ``[0, 1]`` and
    ``cosh(n*acosh(u))`` beyond 1. On ``[0, 1]``, ``G_n`` ripples ``n`` times between ``1/sqrt(2)`` and 1; beyond 1 it
    falls faster than the Butterworth filter's gain of the same order, over a width of about ``1/n^2``. ``G_n`` is even,
    so the interval starts at 0 and leaves out the mirror image of the root.

    - ``n`` is an integer of at least 1, the order.
    - ``d`` is the level, between 0 and 1. Below ``1/sqrt(2)`` the root lies on the falling side beyond the cutoff,
      within the step or, for a small ``d``, in its tail. Between ``1/sqrt(2)`` and 1, the level crosses the ripples, so
      the interval holds about ``n`` roots.

    A pair of ``n`` and ``d`` is valid only when the function changes sign on the interval at ``c = 0``: ``d`` lies
    below ``G_n(0)``, which is 1 for an odd ``n`` and ``1/sqrt(2)`` for an even one, and above ``G_n(2)``.

    Beyond the cutoff, the function computes ``G_n`` as ``2*v/sqrt(1 + 6*v^2 + v^4)`` with ``v = exp(-n*acosh(u))``,
    which underflows to 0 for a large ``n`` where ``cosh(n*acosh(u))`` would overflow: without numba's compilation,
    Python raises on that overflow.

    ``c`` shifts x, so the roots at ``c = 0`` move by ``c``.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the Chebyshev polynomial ``T_n``.
          https://dlmf.nist.gov/18.3
    """

    number = (2, 7, 7)
    name = "Chebyshev filter gain"
    params = (
        FormulaParam("n", latex_symbol="n", meaning="The order of the filter."),
        FormulaParam("d", latex_symbol="d", meaning="The level, between the gain's maximum 1 and its tail at 0."),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"|\x - \c|"),),
        expression=(
            r"\begin{cases} "
            r"\frac{1}{\sqrt{1 + \cos(\param{n} \arccos(\tmp{u}))^2}} - \param{d} & \text{if } \tmp{u} \le 1 \\ "
            r"\frac{2 e^{-\param{n} \operatorname{arcosh}(\tmp{u})}}"
            r"{\sqrt{1 + 6 e^{-2 \param{n} \operatorname{arcosh}(\tmp{u})} "
            r"+ e^{-4 \param{n} \operatorname{arcosh}(\tmp{u})}}}"
            r" - \param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 2]",
        summary=(
            "The gain of the Chebyshev filter, which ripples with equal heights and then falls in a steep step, with "
            "the root in the step or its tail or, at a level within the ripples, with many roots among them."
        ),
        notes=(
            (
                r"Both cases equal $$\frac{1}{\sqrt{1 + T_{\param{n}}(\tmp{u})^2}} - \param{d},$$ with the Chebyshev "
                r"polynomial of the first kind $T_{\param{n}}$, which is "
                r"$\cosh(\param{n} \operatorname{arcosh}(\tmp{u}))$ for $\tmp{u} > 1$; the second case keeps every "
                r"exponential at or below 1, so that no value overflows at a high order."
            ),
        ),
        param_conditions=(
            r"$\param{n}$ is an integer of at least 1",
            (
                r"$\param{d}$ lies between the function's values at $\x - \c = 2$ and at $\x - \c = 0$, before "
                r"$\param{d}$ is subtracted, so that the function changes sign on the interval"
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, d: float) -> float:
        """Evaluate ``G_n(x - c) - d``, in the form that never overflows."""
        u = abs(x - c)
        if u <= 1.0:
            t = math.cos(n * math.acos(u))
            return 1.0 / math.sqrt(1.0 + t * t) - d
        else:
            v = math.exp(-n * math.acosh(u))
            return 2.0 * v / math.sqrt(1.0 + 6.0 * v * v + v**4) - d

    def interval_bounds(self, n: float, d: float) -> tuple[float, float]:
        """Return the interval ``[0, 2]``."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 3 recipes: one that sweeps ``n`` at ``d = 1/2``, and 2 that sweep ``d`` below and within the ripples.

        - The sweep of ``n``: from 1 to 2^20. From about 2^20 on, the step, about ``1/n^2`` wide, is narrower than the
          benchmark's ``xtol``, so every solver sees the Heaviside step at ``d = 1/2``.
        - The sweep of ``d`` below the ripples, at ``n = 2^16``: from 2^-19 to 1/2. Below 2^-19 the core solver
          configs spend about as many evaluations at every ``d``.
        - The sweep of ``d`` within the ripples, at ``n = 65``: from 0.71 to 0.99. An odd ``n`` keeps the function
          positive at 0. At a larger ``n``, the c-range of a level close to 1 would be narrower than validation allows,
          because each bound lies within 1 ripple of a root.
        """
        return (
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 20.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),
                    ParamAxis("d", -1.0, -1.0, 1.0, ParamNotation.POW2),
                ),
                summary=(
                    r"The values of $\param{n}$ nearest to $2^{0.1 i}$, for $i$ from 0 to 200, each once, at "
                    r"$\param{d} = \frac{1}{2}$."
                ),
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 16.0, 16.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -19.0, -1.0, 0.2, ParamNotation.POW2),
                ),
                summary=r"The sweep of $\param{d}$ from $2^{-19}$ to $\frac{1}{2}$ at $\param{n} = 2^{16}$.",
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 6.0, 6.0, 1.0, ParamNotation.POW2, ParamRounding.NEAREST_ODD_INTEGER),
                    ParamAxis("d", 0.71, 0.99, 0.01),
                ),
                summary=r"The sweep of $\param{d}$ from 0.71 to 0.99 at $\param{n} = 65$, within the ripples.",
            ),
        )

    def is_param_tuple_valid(self, n: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        if n >= 1.0 and n == math.floor(n):
            return self.parametrized_fun(2.0, 0.0, n, 0.0) < d < self.parametrized_fun(0.0, 0.0, n, 0.0)
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"n": 3.0, "d": 0.5}, x=0.0, c=0.0, expected=0.5),  # T_3(0) = 0
        FormulaTestCase.value(params={"n": 3.0, "d": 0.5}, x=1.0, c=0.0, expected=1.0 / math.sqrt(2.0) - 0.5),
        # T_2(1/2) = 2*(1/2)^2 - 1 = -1/2
        FormulaTestCase.value(params={"n": 2.0, "d": 0.5}, x=0.5, c=0.0, expected=1.0 / math.sqrt(1.25) - 0.5),
        # T_2(3/2) = 2*(3/2)^2 - 1 = 7/2, beyond the cutoff
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=1.5, c=0.0, expected=1.0 / math.sqrt(13.25) - 0.25),
        FormulaTestCase.value(params={"n": 2.0**20, "d": 0.25}, x=2.0, c=0.0, expected=-0.25),  # v is 0
        FormulaTestCase.value(params={"n": 3.0, "d": 0.5}, x=1.25, c=0.25, expected=1.0 / math.sqrt(2.0) - 0.5),
        FormulaTestCase.invalid(params={"n": 0.0, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 1.5, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 2.0, "d": 0.8}),  # G_2(0) is 1/sqrt(2), below the level
        FormulaTestCase.invalid(params={"n": 1.0, "d": 0.25}),  # G_1(2) is 1/sqrt(5), above the level
        FormulaTestCase.interval_bounds(params={"n": 3.0, "d": 0.5}, expected=(0.0, 2.0)),
    )
