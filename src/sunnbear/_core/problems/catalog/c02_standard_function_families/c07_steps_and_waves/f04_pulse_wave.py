"""This formula is the zero-mean pulse wave of duty cycle ``d``, whose sign changes at ``2*n + 1`` jumps."""

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


class PulseWave(Formula):
    """`PulseWave` is ``p(x - c)`` on ``[-(1 - d)/2, n + d/2]``, with the pulse wave ``p`` of duty cycle ``d``.

    ``p(u)`` is ``1 - d`` where ``u - floor(u) < d`` and ``-d`` elsewhere, so its mean over a period is 0.

    It jumps up
    at each integer and down at each ``k + d``, and takes no value 0, so every sign change lies at a jump, where the
    function has no root. At ``d = 1/2`` it is half the square wave.

    - ``n`` is an integer of at least 1. The interval holds the ``2*n + 1`` jumps from the up-jump at 0 to the up-jump
      at ``n``; its lower bound lies halfway along a low part, and its upper bound halfway along a high part. At
      ``n = 0`` the interval would hold 1 jump, and the function would be the Heaviside step at the same ``d``.
    - ``d`` lies between 0 and 1/2: it is the duty cycle, and the levels are ``-d`` and ``1 - d``, as the Heaviside
      step's are. ``d`` and ``1 - d`` give mirror images of each other, so ``d`` stays at or below 1/2.

    ``c`` shifts x by ``c`` itself: the c-range is set by the distance from the upper bound to the nearest jump, which
    is ``d/2`` at every ``n``.
    """

    number = (2, 7, 4)
    name = "Pulse wave"
    params = (
        FormulaParam("n", latex_symbol="n", meaning=r"The number of periods between the first and the last up-jump."),
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=(
                r"The duty cycle, and the distance of the lower level below 0; the upper level lies at "
                r"$1 - \param{d}$."
            ),
        ),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} "
            r"1 - \param{d} & \text{if } \tmp{u} - \lfloor \tmp{u} \rfloor < \param{d} \\ "
            r"-\param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"\left[-\frac{1 - \param{d}}{2}, \param{n} + \frac{\param{d}}{2}\right]",
        summary=(
            "The pulse wave with zero mean, whose sign changes at many jumps of alternating direction, where it has "
            "no root, between 2 levels."
        ),
        param_conditions=(r"$\param{n}$ is an integer of at least 1", r"$0 < \param{d} \le \frac{1}{2}$"),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, d: float) -> float:
        """Evaluate ``p(x - c)``."""
        u = x - c
        if u - math.floor(u) < d:
            return 1.0 - d
        else:
            return -d

    def interval_bounds(self, n: float, d: float) -> tuple[float, float]:
        """Return the interval ``[-(1 - d)/2, n + d/2]``."""
        return (-0.5 * (1.0 - d), n + 0.5 * d)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one that sweeps ``d`` at ``n = 2^20``, and one that sweeps ``n`` at ``d = 2^-8``.

        - The sweep of ``d``: from 2^-9 to 1/2. At ``d = 2^-10`` the c-range would be narrower than validation allows.
          ``n = 2^20`` is the ``n`` at which the core solver configs spend their evaluations least like they do on the
          Heaviside step at the same ``d``.
        - The sweep of ``n``: from 1 to 2^20, the ``n`` of the sweep of ``d``, so that the 2 sweeps meet there.
        """
        return (
            ParamGrid(
                axes=(
                    ParamAxis("n", 20.0, 20.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -9.0, -1.0, 0.1, ParamNotation.POW2),
                ),
                summary=r"The sweep of $\param{d}$ from $2^{-9}$ to $\frac{1}{2}$ at $\param{n} = 2^{20}$.",
            ),
            ParamGrid(
                axes=(
                    ParamAxis("n", 0.0, 20.0, 0.25, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),
                    ParamAxis("d", -8.0, -8.0, 1.0, ParamNotation.POW2),
                ),
                summary=(
                    r"The values of $\param{n}$ nearest to $2^{0.25 i}$, for $i$ from 0 to 80, each once, at "
                    r"$\param{d} = 2^{-8}$."
                ),
            ),
        )

    def is_param_tuple_valid(self, n: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return n >= 1.0 and n == math.floor(n) and 0.0 < d <= 0.5

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=0.125, c=0.0, expected=0.75),  # a high part
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=0.5, c=0.0, expected=-0.25),  # a low part
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=1.0, c=0.0, expected=0.75),  # at an up-jump
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=0.25, c=0.0, expected=-0.25),  # at a down-jump
        FormulaTestCase.value(params={"n": 2.0, "d": 0.25}, x=0.375, c=0.25, expected=0.75),  # c moves the jumps
        FormulaTestCase.invalid(params={"n": 0.0, "d": 0.25}),
        FormulaTestCase.invalid(params={"n": 1.5, "d": 0.25}),
        FormulaTestCase.invalid(params={"n": 2.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"n": 2.0, "d": 0.75}),
        FormulaTestCase.interval_bounds(params={"n": 2.0, "d": 0.25}, expected=(-0.375, 2.125)),
    )
