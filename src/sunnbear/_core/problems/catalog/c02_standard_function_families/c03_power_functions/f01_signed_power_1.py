"""This formula is a signed power of ``z = x - c/(1 + p)`` plus a tiny linear term, so its root moves with ``c``."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamGrid,
    ParamRecipe,
)
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE

from .helpers import power_axis


class SignedPower1(Formula):
    """`SignedPower1` is ``sign(z)*abs(z)^p + TINY_LINEAR_TERM_SLOPE*z`` with ``z = x - c/(1 + p)``, on ``[-1, 1]``.

    The signed power ``sign(z)*abs(z)^p`` extends the power ``z^p`` to a negative ``z`` for a ``p`` that is not an
    integer. It is increasing, and odd-symmetric about its root ``z = 0``:

    - below ``p = 1``, its slope at the root is infinite, as for a square root;
    - at ``p = 1``, it is the line ``z``;
    - above ``p = 1``, it is flat at the root.

    ``p`` is the power, any value above 0.

    ``c`` shifts x, so the root lies at ``x = c/(1 + p)``, and the function has the same form around its root for
    every ``c``.

    The shift is ``c/(1 + p)``, not ``c``, so that the values at the bounds, ``(1 - c/(1 + p))^p`` and
    ``-(1 + c/(1 + p))^p``, stay about ``exp(-c)`` and ``-exp(c)`` for every large ``p``. The calibrated range of ``c``
    then does not shrink as ``p`` grows.

    The linear term keeps the function from being exactly 0 around its root. For a large ``p``, ``abs(z)^p`` underflows
    to 0 in float64 on an interval around the root.

    Without the term, the test problem would not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too.

    The larger ``p`` is, the larger the part of the interval around the root where the power is below
    ``TINY_LINEAR_TERM_SLOPE*abs(z)``. On that part the function is about the line ``TINY_LINEAR_TERM_SLOPE*z``, and
    the power dominates only next to the bounds.
    """

    number = (2, 3, 1)
    name = "Signed power 1"
    params = (FormulaParam("p", latex_symbol="p"),)
    presentation = FormulaPresentation(
        definitions=((r"\tmp{z}", r"\x - \frac{\c}{1 + \param{p}}"),),
        expression=r"\operatorname{sgn}(\tmp{z}) \, |\tmp{z}|^{\param{p}} + 2^{-918} \, \tmp{z}",
        interval="[-1, 1]",
        summary=(
            r"A signed power, with an infinite slope at its root for $\param{p} < 1$ and a zero slope for "
            r"$\param{p} > 1$."
        ),
        notes=(
            r"The term $2^{-918} \, \tmp{z}$ keeps the function from being exactly 0 next to its root, where "
            r"$|\tmp{z}|^{\param{p}}$ underflows to 0 for a large $\param{p}$.",
        ),
        param_conditions=(r"$\param{p} > 0$",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float) -> float:
        """Evaluate ``sign(z)*abs(z)^p + TINY_LINEAR_TERM_SLOPE*z`` at ``z = x - c/(1 + p)``."""
        z = x - c / (1.0 + p)
        return math.copysign(abs(z) ** p, z) + TINY_LINEAR_TERM_SLOPE * z

    def interval_bounds(self, p: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``p`` from 10^-6 to 10^6.

        At the low end the function is close to the step ``sign(z)``. At the high end the power exceeds the linear
        term only in a narrow strip at each bound.
        """
        return (
            ParamGrid(axes=(power_axis(-6.0, 6.0),), summary=r"The sweep of $\param{p}$ from $10^{-6}$ to $10^{6}$."),
        )

    def is_param_tuple_valid(self, p: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return p > 0.0

    test_cases = (
        FormulaTestCase.value(params={"p": 2.0}, x=0.5, c=0.0, expected=0.25),
        FormulaTestCase.value(params={"p": 0.5}, x=-0.25, c=0.0, expected=-0.5),  # the sign of z
        FormulaTestCase.value(params={"p": 3.0}, x=1.0, c=2.0, expected=0.125),  # z = 1 - 2/4
        FormulaTestCase.value(params={"p": 3.0}, x=0.5, c=2.0, expected=0.0),  # the root, at x = c/(1 + p)
        # 0.5^2000 underflows to 0, so only the linear term is left
        FormulaTestCase.value(
            params={"p": 2000.0}, x=0.5, c=0.0, expected=0.5 * TINY_LINEAR_TERM_SLOPE, rtol=1e-12, atol=0.0
        ),
        FormulaTestCase.invalid(params={"p": 0.0}),
        FormulaTestCase.invalid(params={"p": -2.0}),
        FormulaTestCase.interval_bounds(params={"p": 2.0}, expected=(-1.0, 1.0)),
    )
