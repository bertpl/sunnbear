"""This formula is the generalized smoothstep of order ``n``, a polynomial step between exactly constant plateaus."""

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


class Smoothstep(Formula):
    """`Smoothstep` is ``S_n(x - b*c + 1/2) - d`` on ``[-b, b]``, with the generalized smoothstep ``S_n``.

    ``S_n(t)`` is 0 for ``t <= 0``, 1 for ``t >= 1``, and in between the polynomial of degree ``2*n + 1`` whose first
    ``n`` derivatives vanish at both ends: ``S_0`` is the clamped line, ``S_1(t) = 3*t^2 - 2*t^3`` the classic
    smoothstep of computer graphics, ``S_2(t) = 6*t^5 - 15*t^4 + 10*t^3`` the "smootherstep". The function is exactly
    ``-d`` and ``1 - d`` on either side of the step, at any steepness.

    Between 0 and 1, the function sums the Bernstein form of ``S_n``,
    ``sum(j = n+1 … 2*n+1) C(2*n + 1, j) * t^j * (1 - t)^(2*n + 1 - j)``: its terms are positive, so none cancels
    another, and each comes from log-gamma, so no binomial coefficient overflows. Each evaluation sums ``n + 1`` terms,
    so its cost grows with ``n``.

    - ``n`` is an integer of at least 0, the order.
    - ``b`` is the upper bound of the interval, at least 1/2. At ``c = 0`` the step lies on ``[-1/2, 1/2]``, so ``b``
      sets the interval's width relative to the step's: at ``b = 1/2`` the interval is the step itself; for a large
      ``b``, the function is close to the Heaviside step.
    - ``d`` is the level, between 0 and 1/2. ``S_n(1 - t) = 1 - S_n(t)``, so ``d`` and ``1 - d`` give mirror images of
      each other, and ``d`` stays at or below 1/2.

    ``c`` shifts x by ``b*c``, so the c-range is close to the same for every ``b``.
    """

    number = (2, 7, 8)
    name = "Smoothstep"
    params = (
        FormulaParam(
            "n",
            latex_symbol="n",
            meaning="The order: the number of derivatives that vanish at both ends of the step.",
        ),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("d", latex_symbol="d", meaning="The level, between the plateaus 0 and 1."),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{t}", r"\x - \param{b} \c + \frac{1}{2}"),),
        expression=(
            r"\begin{cases} "
            r"-\param{d} & \text{if } \tmp{t} \le 0 \\ "
            r"1 - \param{d} & \text{if } \tmp{t} \ge 1 \\ "
            r"\sum_{j=\param{n}+1}^{2 \param{n}+1} \binom{2 \param{n}+1}{j} \tmp{t}^j (1 - \tmp{t})^{2 \param{n}+1-j} "
            r"- \param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[-\param{b}, \param{b}]",
        summary=(
            "The generalized smoothstep, a polynomial step whose first derivatives vanish at both ends, between "
            "plateaus that are exactly constant, with the root in the step or next to its lower end."
        ),
        notes=(
            (
                r"Between 0 and 1, the sum is the polynomial of degree $2 \param{n} + 1$ whose first $\param{n}$ "
                r"derivatives vanish at $\tmp{t} = 0$ and $\tmp{t} = 1$; at order 1 it is $3 \tmp{t}^2 - 2 \tmp{t}^3$."
            ),
        ),
        param_conditions=(
            r"$\param{n}$ is an integer of at least 0",
            r"$\param{b} \ge \frac{1}{2}$",
            r"$0 < \param{d} \le \frac{1}{2}$",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, b: float, d: float) -> float:
        """Evaluate ``S_n(x - b*c + 1/2) - d``, with ``S_n`` in its Bernstein form between 0 and 1."""
        t = x - b * c + 0.5
        if t <= 0.0:
            return -d
        elif t >= 1.0:
            return 1.0 - d
        else:
            m = 2 * int(n) + 1
            log_t = math.log(t)
            log_1_minus_t = math.log1p(-t)
            log_m_factorial = math.lgamma(m + 1.0)
            total = 0.0
            for j in range(int(n) + 1, m + 1):
                log_binomial = log_m_factorial - math.lgamma(j + 1.0) - math.lgamma(m - j + 1.0)
                total += math.exp(log_binomial + j * log_t + (m - j) * log_1_minus_t)
            return total - d

    def interval_bounds(self, n: float, b: float, d: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the sweeps of ``b``, ``n`` and ``d``, each at the other 2 of ``n = 1``, ``b = 2^10`` and ``d = 1/2``.

        - The sweep of ``b``: from 1/2 to 2^40. From about 2^40 on, the step is narrower than the benchmark's ``xtol``,
          so every solver sees the Heaviside step at ``d = 1/2``. Its steps are coarser than the other sweeps', because
          the core solver configs spend their evaluations about as on the Butterworth filter's gain over its order.
        - The sweep of ``n``, in 2 grids: ``n = 0``, the clamped line, and the integers from 1 to 2^10. Each
          evaluation sums ``n + 1`` terms.
        - The sweep of ``d``: from 2^-40 to 1/2. Below 2^-40, the core solver configs spend their evaluations in about
          the same pattern as on the Heaviside step.
        """
        return (
            ParamGrid(
                axes=(
                    ParamAxis("n", 1.0, 1.0, 1.0),
                    ParamAxis("b", -1.0, 40.0, 0.5, ParamNotation.POW2),
                    ParamAxis("d", -1.0, -1.0, 1.0, ParamNotation.POW2),
                ),
                summary=(
                    r"The sweep of $\param{b}$ from $\frac{1}{2}$ to $2^{40}$ at $\param{n} = 1$, "
                    r"$\param{d} = \frac{1}{2}$."
                ),
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 0.0, 1.0),
                    ParamAxis("b", 10.0, 10.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -1.0, -1.0, 1.0, ParamNotation.POW2),
                ),
                summary=r"The clamped line, $\param{n} = 0$, at $\param{b} = 2^{10}$, $\param{d} = \frac{1}{2}$.",
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 10.0, 0.25, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),
                    ParamAxis("b", 10.0, 10.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -1.0, -1.0, 1.0, ParamNotation.POW2),
                ),
                summary=(
                    r"The values of $\param{n}$ nearest to $2^{0.25 i}$, for $i$ from 0 to 40, each once, at "
                    r"$\param{b} = 2^{10}$, $\param{d} = \frac{1}{2}$."
                ),
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 1.0, 1.0, 1.0),
                    ParamAxis("b", 10.0, 10.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -40.0, -1.0, 0.25, ParamNotation.POW2),
                ),
                summary=(
                    r"The sweep of $\param{d}$ from $2^{-40}$ to $\frac{1}{2}$ at $\param{n} = 1$, "
                    r"$\param{b} = 2^{10}$."
                ),
            ),
        )

    def is_param_tuple_valid(self, n: float, b: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return n >= 0.0 and n == math.floor(n) and b >= 0.5 and 0.0 < d <= 0.5

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0, "b": 4.0, "d": 0.5}, x=0.0, c=0.0, expected=0.0),  # the root
        FormulaTestCase.value(params={"n": 1.0, "b": 4.0, "d": 0.5}, x=-1.0, c=0.0, expected=-0.5),  # a plateau
        FormulaTestCase.value(params={"n": 1.0, "b": 4.0, "d": 0.5}, x=1.0, c=0.0, expected=0.5),  # the other
        # S_1(1/4) = 3/16 - 2/64 = 5/32, S_2(1/4) = 6/1024 - 15/256 + 10/64 = 106/1024, S_0(1/4) = 1/4
        FormulaTestCase.value(params={"n": 1.0, "b": 4.0, "d": 0.125}, x=-0.25, c=0.0, expected=5.0 / 32.0 - 0.125),
        FormulaTestCase.value(params={"n": 2.0, "b": 4.0, "d": 0.125}, x=-0.25, c=0.0, expected=106.0 / 1024.0 - 0.125),
        FormulaTestCase.value(params={"n": 0.0, "b": 4.0, "d": 0.125}, x=-0.25, c=0.0, expected=0.25 - 0.125),
        FormulaTestCase.value(
            params={"n": 1.0, "b": 4.0, "d": 0.5}, x=2.0, c=0.5, expected=0.0
        ),  # c moves the step by b*c
        FormulaTestCase.invalid(params={"n": -1.0, "b": 4.0, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 1.5, "b": 4.0, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 1.0, "b": 0.25, "d": 0.5}),
        FormulaTestCase.invalid(params={"n": 1.0, "b": 4.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"n": 1.0, "b": 4.0, "d": 0.75}),
        FormulaTestCase.interval_bounds(params={"n": 1.0, "b": 4.0, "d": 0.5}, expected=(-4.0, 4.0)),
    )
