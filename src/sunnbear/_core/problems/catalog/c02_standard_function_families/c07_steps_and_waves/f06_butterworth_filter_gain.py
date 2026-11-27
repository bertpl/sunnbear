"""This formula is the gain of the Butterworth filter of order ``n``, maximally flat at 0 and a steep step at 1."""

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


class ButterworthFilterGain(Formula):
    """`ButterworthFilterGain` is ``G_n(x - c) - d`` on ``[0, 2]``, with the gain ``G_n(u) = 1/sqrt(1 + abs(u)^(2*n))``.

    ``G_n`` is the gain of the Butterworth low-pass filter of order ``n``, at the frequency ``u`` relative to its
    cutoff:

    - it is 1 at 0, where its first ``2*n - 1`` derivatives vanish;
    - it falls through ``1/sqrt(2)`` at ``u = 1`` for every ``n``;
    - it decays as ``u^(-n)`` beyond 1.

    For a large ``n``, ``G_n`` is close to a step at 1, and in float64 it is exactly 1 on most of ``[0, 1)`` and
    exactly 0 on most of ``(1, 2]``. ``G_n`` is even, so the interval starts at its maximum and leaves out the mirror
    image of the root.

    - ``n`` is an integer of at least 1, the order.
    - ``d`` is the level, between 0 and 1/2, so the root lies on the falling side at or beyond the cutoff: at
      ``d = 1/2`` within the step, for a small ``d`` in the tail beyond it. A level above 1/2 would put the root on the
      flat top, where ``G_n - d`` subtracts 2 values close to 1.

    A pair of ``n`` and ``d`` is valid only when the root at ``c = 0``, ``u = (1/d^2 - 1)^(1/(2*n))``, lies inside the
    interval.

    ``c`` shifts x, so the root at ``c = 0`` moves by ``c``.
    """

    number = (2, 7, 6)
    name = "Butterworth filter gain"
    params = (
        FormulaParam("n", latex_symbol="n", meaning="The order of the filter."),
        FormulaParam("d", latex_symbol="d", meaning="The level, between the gain's plateaus 1 and 0."),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"|\x - \c|"),),
        expression=(
            r"\begin{cases} "
            r"\frac{1}{\sqrt{1 + \tmp{u}^{2 \param{n}}}} - \param{d} & \text{if } \tmp{u} \le 1 \\ "
            r"\frac{\tmp{u}^{-\param{n}}}{\sqrt{1 + \tmp{u}^{-2 \param{n}}}} - \param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 2]",
        summary=(
            "The gain of the Butterworth filter, maximally flat at its maximum; for a high order it is a steep step "
            "with a tail that decays as a power, and the root lies in the step or in its tail."
        ),
        notes=(
            r"Both cases equal $$\frac{1}{\sqrt{1 + |\x - \c|^{2 \param{n}}}} - \param{d};$$ the second keeps every "
            r"power at or below 1, so that no value overflows at a high order.",
        ),
        param_conditions=(
            r"$\param{n}$ is an integer of at least 1",
            r"$0 < \param{d} \le \frac{1}{2}$",
            (
                r"$\left(\frac{1}{\param{d}^2} - 1\right)^{1 / (2 \param{n})} < 2$, so that the root lies inside the "
                r"interval"
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, d: float) -> float:
        """Evaluate ``G_n(x - c) - d``, in the form that never overflows.

        Beyond ``abs(u) = 1``, the function computes ``G_n`` as ``s/sqrt(1 + s^2)`` with ``s = abs(u)^(-n)``. For a
        large ``n``, ``s`` underflows to 0 where ``abs(u)^(2*n)`` would overflow, and plain Python, unlike
        numba-compiled code, raises on that overflow.
        """
        u = abs(x - c)
        if u <= 1.0:
            return 1.0 / math.sqrt(1.0 + u ** (2.0 * n)) - d
        else:
            s = u ** (-n)
            return s / math.sqrt(1.0 + s * s) - d

    def interval_bounds(self, n: float, d: float) -> tuple[float, float]:
        """Return the interval ``[0, 2]``."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one that sweeps ``n`` at ``d = 1/2``, and one that sweeps ``d`` at ``n = 2^20``.

        - The sweep of ``n``: from 1 to 2^40. From about 2^40 on, the step, about ``1/n`` wide, is narrower than the
          benchmark's ``xtol``, so every solver behaves as it does on the Heaviside step at ``d = 1/2``.
        - The sweep of ``d``: from 2^-21 to 1/2. Below 2^-21 the core solver configs spend about as many evaluations
          at every ``d``.
        """
        return (
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 40.0, 0.25, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),
                    ParamAxis("d", -1.0, -1.0, 1.0, ParamNotation.POW2),
                ),
                summary=(
                    r"The values of $\param{n}$ nearest to $2^{0.25 i}$, for $i$ from 0 to 160, each once, at "
                    r"$\param{d} = \frac{1}{2}$."
                ),
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 20.0, 20.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -21.0, -1.0, 0.2, ParamNotation.POW2),
                ),
                summary=r"The sweep of $\param{d}$ from $2^{-21}$ to $\frac{1}{2}$ at $\param{n} = 2^{20}$.",
            ),
        )

    def is_param_tuple_valid(self, n: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        if n >= 1.0 and n == math.floor(n) and 0.0 < d <= 0.5:
            return (1.0 / d**2 - 1.0) ** (1.0 / (2.0 * n)) < 2.0
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0, "d": 0.5}, x=math.sqrt(3.0), c=0.0, expected=0.0),  # the root
        FormulaTestCase.value(params={"n": 4.0, "d": 0.5}, x=1.0, c=0.0, expected=1.0 / math.sqrt(2.0) - 0.5),
        FormulaTestCase.value(params={"n": 4.0, "d": 0.5}, x=0.0, c=0.0, expected=0.5),  # the maximum
        FormulaTestCase.value(params={"n": 2.0**40, "d": 0.25}, x=2.0, c=0.0, expected=-0.25),  # u^(-n) is 0
        FormulaTestCase.value(
            params={"n": 2.0, "d": 0.25}, x=1.5, c=0.0, expected=1.0 / math.sqrt(1.0 + 1.5**4) - 0.25
        ),
        FormulaTestCase.value(params={"n": 4.0, "d": 0.5}, x=1.25, c=0.25, expected=1.0 / math.sqrt(2.0) - 0.5),
        FormulaTestCase.invalid(params={"n": 0.0, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 1.5, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 4.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"n": 4.0, "d": 0.75}),
        FormulaTestCase.invalid(params={"n": 1.0, "d": 2.0**-10}),  # the root lies at about 1024
        FormulaTestCase.interval_bounds(params={"n": 4.0, "d": 0.5}, expected=(0.0, 2.0)),
    )
