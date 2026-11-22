"""This module holds formula f1.99.2.13.9, the modified version of the published formula f1.2.13.9.

A change of formula f1.2.13.9 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedSabharwal2019Function8(Formula):
    """This formula is the modified version of formula f1.2.13.9, from Sabharwal (2019).

    The survey writes the source's function as ``x*exp(x) - 7``; the published interval is ``[-1, 1]``.

    Printed `xe^x - 7`. No sign change and no root on `[-1, 1]`: the only real root is about `1.5243`.

    The formula changes the published interval ``[-1, 1]`` to ``[-1, 2]``: its upper bound moves right of the function's
    root, near 1.52, so that the interval holds that root. ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the root lies outside
    the published interval, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 2, 13, 9)
    name = "Function 8"
    params = ()
    location_in_publication = "Table 2, function 8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 7",
        interval="[-1, 2]",
        notes=(
            (
                "The interval ends at 2, not at the published 1, so that it holds the function's root, "
                "near 1.52, which the published interval leaves out."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.25, expected=-7.3633026921564175),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
