"""This formula is the sawtooth wave ``s(x - c)``, whose roots on its ramps alternate with sign changes at its jumps."""

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


class SawtoothWave(Formula):
    """`SawtoothWave` is ``s(x - c)`` on ``[-(n + 1/4), n + 1/4]``, with the sawtooth wave ``s``.

    ``s(u) = u - floor(u + 1/2)`` rises with slope 1 from -1/2 to 1/2 on each tooth, and jumps back down to -1/2 at
    each half-integer. The interval holds the ``2*n + 1`` roots at the integers from ``-n`` to ``n``, and the ``2*n``
    jumps between them, where the function changes sign too, without a root. Its bounds lie halfway between a root and
    the next jump, where the function is -1/4 and 1/4.

    ``n`` is an integer of at least 1. A solver halves the interval until it holds 1 tooth, then finds the root on the
    tooth's ramp, which is a line, in a few evaluations; the jumps seldom end a solve. At ``n = 0`` the function is a
    line, as `Linear` is.

    ``c`` shifts x by ``c`` itself: the c-range is set by the distance from a bound to the nearest root, which is the
    same for every ``n``.
    """

    number = (2, 7, 3)
    name = "Sawtooth wave"
    params = (
        FormulaParam("n", latex_symbol="n", meaning=r"The number of teeth on each side of the root at $\x = \c$."),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} - \left\lfloor \tmp{u} + \frac{1}{2} \right\rfloor",
        interval=r"\left[-\left(\param{n} + \frac{1}{4}\right), \param{n} + \frac{1}{4}\right]",
        summary=(
            "The sawtooth wave, with many roots on ramps of slope 1 and, between them, as many jumps at which the sign "
            "changes without a root."
        ),
        param_conditions=(r"$\param{n}$ is an integer of at least 1",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``s(x - c)``."""
        u = x - c
        return u - math.floor(u + 0.5)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the interval ``[-(n + 1/4), n + 1/4]``."""
        return (-(n + 0.25), n + 0.25)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe of the integers ``n`` nearest to 2^(0.1*i), for i from 0 to 200.

        The sweep ends at the round value 2^20: from about there on, a bisection midpoint lands exactly on a root at a
        few of the benchmark's tuples for many values of ``n``, and validation rejects those values.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("n", 0.0, 20.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),),
                summary=r"The values of $\param{n}$ nearest to $2^{0.1 i}$, for $i$ from 0 to 200, each once.",
            ),
        )

    def is_param_tuple_valid(self, n: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return n >= 1.0 and n == math.floor(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.0, c=0.0, expected=0.0),  # the root at 0
        FormulaTestCase.value(params={"n": 2.0}, x=1.25, c=0.0, expected=0.25),  # halfway up a ramp
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.0, expected=-0.5),  # at a jump, the lower end
        FormulaTestCase.value(params={"n": 2.0}, x=-2.25, c=0.0, expected=-0.25),  # the lower bound
        FormulaTestCase.value(params={"n": 2.0}, x=1.25, c=0.25, expected=0.0),  # c moves the roots to k + c
        FormulaTestCase.invalid(params={"n": 0.0}),
        FormulaTestCase.invalid(params={"n": 1.5}),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(-2.25, 2.25)),
    )
