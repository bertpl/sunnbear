"""This module holds formula f1.99.1.5.3, the modified version of the published formula f1.1.5.3.

A change of formula f1.1.5.3 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedRidders1979Function2(Formula):
    """This formula is the modified version of formula f1.1.5.3, from Ridders (1979).

    The survey writes the source's function as ``tan(x)^tan(x) - 10^3``; the published intervals are `[1.3, 1.4]`;
    `[0, 1.5]`.

    Last printed iterate: `1.354710442`.

    The formula holds only the test problem on ``[0, 1.5]``. The interval ``[0, 1.5]`` becomes ``[0.02, 1.5]``: its
    lower bound moves right of 0 by 1% of the published interval's width, rounded half up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[0, 1.5]`` does not satisfy the benchmark suite inclusion conditions, because a
    shift along x by any ``c > 0`` evaluates ``tan(x)^tan(x)`` left of ``a = 0``, where the base ``tan(x)`` is negative.
    """

    number = (1, 99, 1, 5, 3)
    name = "Function 2"
    params = ()
    location_in_publication = "Section III, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.48 \c"),),
        expression=r"\tan^{\tan{\left(\tmp{u} \right)}}{\left(\tmp{u} \right)} - 10^{3}",
        interval="[0.02, 1.5]",
        summary=(
            "A function within 1% of $-1000$ until 0.2 below its 1 root, then rising steeply through that root toward a"
            " pole 0.22 above the root."
        ),
        notes=(
            (
                "The interval starts at 0.02, not at the published 0, because a shift along x evaluates "
                r"the function left of 0, where its base, $\tan(\tmp{u})$, is negative."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.48 * c
        return math.tan(x) ** math.tan(x) - 10**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.02, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.464, c=0.25, expected=-999.1995954429276),
        FormulaTestCase.interval_bounds(params={}, expected=(0.02, 1.5)),
    )
