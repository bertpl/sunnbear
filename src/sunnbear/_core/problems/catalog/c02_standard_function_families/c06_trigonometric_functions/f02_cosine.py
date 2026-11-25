"""This formula is the cosine minus a level, ``cos(0.5*pi*x*exp(-c)) - cos(0.5*pi*d)``, with its root at ``x = d``."""

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


class Cosine(Formula):
    """`Cosine` is ``cos(0.5*pi*x*exp(-c)) - cos(0.5*pi*d)`` on ``[0, 2]``.

    The scale ``0.5*pi`` puts the zeros of the cosine at the odd integers and its extrema at the even integers, so the
    interval runs from a maximum at its lower bound to a minimum at its upper bound.

    ``d`` is the root at ``c = 0``, above 0 and at most 1. The cosine is even, so ``-d`` is a root too, which the
    interval leaves out. At ``d = 1`` the function is the plain cosine, whose root is an inflection point, as every
    root of the sine is. As ``d`` falls, the root moves toward the maximum: the slope at the root falls with ``d``,
    and the roots ``d`` and ``-d`` come close to a double root.

    ``c`` scales x about the maximum, so the root moves to ``x = d*exp(c)``, while the maximum stays at the lower bound
    and the root ``-d`` outside the interval. A shift of x would move the maximum and the root ``-d`` into the
    interval, so the range of ``c`` that keeps the sign at both bounds would shrink with ``d``.

    References:
        - NIST Digital Library of Mathematical Functions, §4.14, for the definition. https://dlmf.nist.gov/4.14
    """

    number = (2, 6, 2)
    name = "Cosine"
    params = (
        FormulaParam("d", latex_symbol="d", meaning=r"The distance from the maximum at 0 to the root, at $\c = 0$."),
    )
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\frac{\pi}{2} \x e^{-\c}"),
            (r"\tmp{v}", r"\frac{\pi}{2} \param{d}"),
        ),
        expression=r"-2 \sin\left(\frac{\tmp{u} + \tmp{v}}{2}\right) \, \sin\left(\frac{\tmp{u} - \tmp{v}}{2}\right)",
        interval="[0, 2]",
        summary=(
            r"The cosine minus a level, with 1 root on the interval, close to a maximum of the cosine for a small "
            r"$\param{d}$, where that root and its mirror image across the maximum come close to a double root."
        ),
        notes=(
            r"The expression equals $$\cos(\tmp{u}) - \cos(\tmp{v}),$$ in a form that loses no precision to "
            "cancellation next to the root.",
        ),
        param_conditions=(r"$0 < \param{d} \le 1$",),
    )
    effect_of_c = EffectOfC.SCALES_X

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``cos(u) - cos(v)`` as ``-2*sin((u + v)/2)*sin((u - v)/2)``.

        Here ``u = 0.5*pi*x*exp(-c)`` and ``v = 0.5*pi*d``, and the 2 forms are equal. Subtracting the 2 values of
        ``cos`` would cancel their leading digits next to the root: for a small ``d`` both values are close to 1, so the
        function would be exactly 0 on a band of x around the root.
        """
        u = 0.5 * math.pi * x * math.exp(-c)
        v = 0.5 * math.pi * d
        return -2.0 * math.sin(0.5 * (u + v)) * math.sin(0.5 * (u - v))

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[0, 2]``, from a maximum of ``cos(0.5*pi*x)`` to the minimum next to it."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``d`` from 2^-30 to 1.

        At ``d = 2^-30`` the slope at the root is about 2e-9, against the function's range of 2 on the interval. Below
        about 2^-33 the range of ``c`` lets the root come too close to the lower bound to satisfy the benchmark suite
        inclusion conditions.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("d", -30.0, 0.0, 0.1, ParamNotation.POW2),),
                summary=r"The sweep of $\param{d}$ from $2^{-30}$ to 1.",
            ),
        )

    def is_param_tuple_valid(self, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return 0.0 < d <= 1.0

    test_cases = (
        FormulaTestCase.value(params={"d": 1.0}, x=1.0, c=0.0, expected=0.0),  # the root at d, an inflection point
        FormulaTestCase.value(params={"d": 1.0}, x=0.0, c=0.0, expected=1.0),  # the maximum
        FormulaTestCase.value(params={"d": 1.0}, x=2.0, c=0.0, expected=-1.0),  # the minimum
        FormulaTestCase.value(params={"d": 0.25}, x=0.25 * math.exp(0.5), c=0.5, expected=0.0),  # c moves the root
        FormulaTestCase.value(
            params={"d": 0.25}, x=0.0, c=0.5, expected=1.0 - math.cos(0.125 * math.pi)
        ),  # c leaves the maximum at 0
        FormulaTestCase.invalid(params={"d": 0.0}),
        FormulaTestCase.invalid(params={"d": 1.5}),
        FormulaTestCase.interval_bounds(params={"d": 0.25}, expected=(0.0, 2.0)),
    )
