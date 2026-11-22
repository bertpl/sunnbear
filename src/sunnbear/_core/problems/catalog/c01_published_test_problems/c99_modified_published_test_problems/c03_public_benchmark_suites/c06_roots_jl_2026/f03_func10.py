"""This module holds formula f1.99.3.6.3, the modified version of the published formula f1.3.6.3.

A change of formula f1.3.6.3 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedRootsJl2026Func10(Formula):
    """This formula is the modified version of formula f1.3.6.3, from Roots.jl (2026).

    The survey writes the source's function as ``asin(x^2 - 1) - x/2 + 1``; the published interval is `[-0.5, 1.0]`
    (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-0.5` to `0.9`.

    The formula changes the interval ``[-0.5, 1]`` to ``[-0.2, 1]``: its lower bound moves right of the first root,
    near -0.30, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.

    The modification changes what the test problem tests: the source gives ``[-0.5, 1]`` to ``find_zeros``, which finds
    every zero in an interval, and a solver on ``[-0.2, 1]`` finds 1 of the 2 roots in ``[-0.5, 1]``.
    """

    number = (1, 99, 3, 6, 3)
    name = "func10"
    params = ()
    location_in_publication = "test_derivative_free.jl, func10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.2 \c"),),
        expression=r"\arcsin{\left(\tmp{u}^{2} - 1 \right)} - \frac{\tmp{u}}{2} + 1",
        interval="[-0.2, 1]",
        notes=(
            (
                "The interval starts at $-0.2$, not at the published $-0.5$, so that it holds 1 of the "
                "published interval's 2 roots: with an even number of roots, the function has the same "
                "sign at both published bounds."
            ),
            (
                "This changes what the test problem tests: the source finds every root in $[-0.5, 1]$, "
                "and a solver on the modified interval finds only 1."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return math.asin(x**2 - 1) - x / 2 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.2, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.16, c=0.25, expected=-0.3024816100652327),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.2, 1.0)),
    )
