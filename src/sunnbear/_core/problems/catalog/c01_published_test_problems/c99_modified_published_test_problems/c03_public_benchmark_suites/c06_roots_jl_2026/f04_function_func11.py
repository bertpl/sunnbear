"""This module holds formula f1.99.3.6.4, the modified version of the published formula f1.3.6.4.

A change of formula f1.3.6.4 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedRootsJl2026FunctionFunc11(Formula):
    """This formula is the modified version of formula f1.3.6.4, from Roots.jl (2026).

    The survey writes the source's function as ``exp(-x) - cos(x)``; the published interval is `[-2, 2]` (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-2.0` to `2.0`.

    The formula changes the interval ``[-2, 2]`` to ``[-2, 1]``: its upper bound moves left of the second root, near
    1.29, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with ``c_scale`` the
    rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.

    The modification changes what the test problem tests: the source gives ``[-2, 2]`` to ``find_zeros``, which finds
    every zero in an interval, and a solver on ``[-2, 1]`` finds 1 of the 2 roots in ``[-2, 2]``.
    """

    number = (1, 99, 3, 6, 4)
    name = "Function func11"
    params = ()
    location_in_publication = "test_derivative_free.jl, func11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{- \tmp{u}} - \cos{\left(\tmp{u} \right)}",
        interval="[-2, 1]",
        summary=(
            "An exponential minus a cosine, steep toward the lower bound, with 1 root and a shallow minimum 0.59 above "
            "that root."
        ),
        notes=(
            (
                "The interval ends at 1, not at the published 2, so that it holds 1 of the published "
                "interval's 2 roots: with an even number of roots, the function has the same sign at both "
                "published bounds."
            ),
            (
                "This changes what the test problem tests: the source finds every root in $[-2, 2]$, and "
                "a solver on the modified interval finds only 1."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(-x) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.75, expected=6.635409769426345),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
