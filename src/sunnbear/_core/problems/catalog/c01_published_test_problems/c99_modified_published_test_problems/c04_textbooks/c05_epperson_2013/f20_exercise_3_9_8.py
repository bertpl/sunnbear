"""This module holds formula f1.99.4.5.20, the modified version of the published formula f1.4.5.20.

A change of formula f1.4.5.20 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEpperson2013Exercise398(Formula):
    """This formula is the modified version of formula f1.4.5.20, from Epperson (2013).

    The survey writes the source's function as ``2*sin(pi*x) + x``; the published interval is ``[1, 2]``.

    By fixed-point iteration.

    The formula changes the published interval ``[1, 2]`` to ``[1.3, 2]``: the lower bound moves right of the first
    root, near 1.21, so that the interval holds 1 of the 2 roots; ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 5, 20)
    name = "Exercise 3.9-8"
    params = ()
    location_in_publication = "Exercise 3.9-8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 \sin{\left(\pi \tmp{u} \right)} + \tmp{u}",
        interval="[1.3, 2]",
        summary=(
            "A function that increases through 1 simple root on the interval, with a local minimum 0.23 to the left of "
            "that root."
        ),
        notes=(
            (
                "The interval starts at 1.3, not at the published 1, so that it holds 1 of the published "
                "interval's 2 roots: with an even number of roots, the function has the same sign at both "
                "published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        return 2 * math.sin(math.pi * x) + x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.3, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.51, c=0.175, expected=-0.40226302887638243),
        FormulaTestCase.interval_bounds(params={}, expected=(1.3, 2.0)),
    )
