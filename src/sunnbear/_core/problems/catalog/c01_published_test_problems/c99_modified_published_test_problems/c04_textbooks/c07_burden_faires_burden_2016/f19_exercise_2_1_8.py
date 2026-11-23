"""This module holds formula f1.99.4.7.19, the modified version of the published formula f1.4.7.19.

A change of formula f1.4.7.19 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurdenFairesBurden2016Exercise218(Formula):
    """This formula is the modified version of formula f1.4.7.19, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = tan(x)``; the published interval is `[4, 5]` (2.2-16).

    The first positive solution by bisection to `1E-5` (2.1-8); the solution in `[4, 5]` by fixed-point iteration to
    `1E-4` (2.2-16).

    The formula changes the published interval ``[4, 5]`` to ``[4, 4.6]``: the upper bound moves left of the pole of
    ``tan(x)`` at ``3*pi/2``, near 4.71, so that the interval holds its root and no pole.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the pole inside the
    published interval is a second sign change, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 7, 19)
    name = "Exercise 2.1-8"
    params = ()
    location_in_publication = "Exercises 2.1-8, 2.2-16"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.6 \c"),),
        expression=r"\tmp{u} - \tan{\left(\tmp{u} \right)}",
        interval="[4, 4.6]",
        notes=(
            (
                "The interval ends at 4.6, not at the published 5, so that it holds the root and no pole. "
                r"The bound 4.6 lies left of the pole of $\tan(\tmp{u})$ at $3\pi/2$, which is a second "
                "sign change, so the function has the same sign at both published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.6 * c
        return (x) - (math.tan(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 4.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.18, c=0.25, expected=2.7994128881553113),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 4.6)),
    )
