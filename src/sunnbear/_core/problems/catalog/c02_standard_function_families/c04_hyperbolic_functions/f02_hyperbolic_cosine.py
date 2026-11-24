"""This formula is the hyperbolic cosine minus its value at the interval's midpoint, ``cosh(x - c) - cosh(b/2)``."""

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
)


class HyperbolicCosine(Formula):
    """`HyperbolicCosine` is ``cosh(x - c) - cosh(b/2)`` on ``[0, b]``.

    ``b`` is the upper bound of the interval, any value above 0.

    ``cosh`` is even, with its minimum at 0, so ``cosh(x) - cosh(b/2)`` has 2 roots, ``-b/2`` and ``b/2``. The interval
    holds the minimum at its lower bound and the root ``b/2`` at its midpoint, and leaves out the root ``-b/2``.

    The function is close to the parabola ``(x^2 - b^2/4)/2`` for a small ``b``, and grows as an exponential toward the
    upper bound for a large ``b``.

    ``c`` shifts x, so the minimum lies at ``x = c`` and the root at ``x = b/2 + c``. A positive ``c`` puts the minimum
    inside the interval, and a negative ``c`` makes the function increase over the whole interval.

    References:
        - NIST Digital Library of Mathematical Functions, §4.28, for the definition. https://dlmf.nist.gov/4.28
    """

    number = (2, 4, 2)
    name = "Hyperbolic cosine"
    params = (FormulaParam("b", latex_symbol="b"),)
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \c"),
            (r"\tmp{v}", r"\frac{\param{b}}{2}"),
        ),
        expression=r"2 \sinh\left(\frac{\tmp{u} + \tmp{v}}{2}\right) \, \sinh\left(\frac{\tmp{u} - \tmp{v}}{2}\right)",
        interval=r"[0, \param{b}]",
        summary=(
            r"The hyperbolic cosine, with its minimum at $\x = \c$ and 1 root on the interval, half the interval's "
            r"width above that minimum."
        ),
        notes=(
            r"The expression equals $$\cosh(\x - \c) - \cosh\left(\frac{\param{b}}{2}\right),$$ in a form that "
            "loses no precision to cancellation next to the root.",
        ),
        param_conditions=(r"$\param{b} > 0$",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``cosh(u) - cosh(v)`` as ``2*sinh((u + v)/2)*sinh((u - v)/2)``, with ``u = x - c`` and ``v = b/2``.

        The 2 forms are equal. Subtracting the 2 values of ``cosh`` would cancel their leading digits next to the root.

        For a small ``b`` both values are close to 1, so the function would be exactly 0 on a band of x around the root,
        and bisection would stop early where a midpoint lands on that band.
        """
        u = x - c
        v = 0.5 * b
        return 2.0 * math.sinh(0.5 * (u + v)) * math.sinh(0.5 * (u - v))

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[0, b]``."""
        return (0.0, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^-1 to 10^2.

        At the high end the value at the upper bound is about 1.3e43.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("b", -1.0, 2.0, 0.02, ParamNotation.POW10),),
                summary=r"The sweep of $\param{b}$ from $10^{-1}$ to $10^{2}$.",
            ),
        )

    def is_param_tuple_valid(self, b: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 2.0}, x=1.0, c=0.0, expected=0.0),  # the root, at x = b/2 + c
        FormulaTestCase.value(params={"b": 2.0}, x=1.5, c=0.5, expected=0.0),
        FormulaTestCase.value(params={"b": 2.0}, x=0.0, c=0.0, expected=1.0 - math.cosh(1.0)),  # the minimum
        FormulaTestCase.value(params={"b": 2.0}, x=2.0, c=-1.0, expected=math.cosh(3.0) - math.cosh(1.0)),
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 2.0}, expected=(0.0, 2.0)),
    )
