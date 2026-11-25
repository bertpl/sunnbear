"""This module holds formula f1.99.4.5.14, the modified version of the published formula f1.4.5.14.

A change of formula f1.4.5.14 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEpperson2013Figure33(Formula):
    """This formula is the modified version of formula f1.4.5.14, from Epperson (2013).

    The survey writes the source's function as ``(4/3)*exp(2 - x/2)*(1 + x^-1*log(x))``; the published interval is `[0,
    8]` (Fig. 3.3).

    Single root near `x = 0.5`. Newton from `x0` in about `[0.8, 1.2]` gives `x1 < 0`, outside the domain; from `x0 >
    1.2` it grows without bound, where `f -> 0`.

    The formula changes the published interval ``[0, 8]`` to ``[0.08, 8]``: the lower bound moves right of 0 by 1% of
    the published interval's width, rounded half up to 1 significant digit; ``c`` shifts x by the rule of category 1,
    with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``log(x)/x`` is not
    finite at ``a = 0``.
    """

    number = (1, 99, 4, 5, 14)
    name = "Figure 3.3"
    params = ()
    location_in_publication = "§3.2 (p. 99), Fig. 3.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=(
            r"\frac{4 e^{2 - \frac{\tmp{u}}{2}} \left(1 + \frac{\ln{\left(\tmp{u} " r"\right)}}{\tmp{u}}\right)}{3}"
        ),
        interval="[0.08, 8]",
        summary=(
            "A function that rises steeply from the lower bound through 1 simple root to a maximum, and then decays "
            "toward 0."
        ),
        notes=(
            (r"The interval starts at 0.08, not at the published 0, where $\ln(\tmp{u})/\tmp{u}$ is not " "finite."),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 10.0 * c
        return (4 / 3) * math.exp(2 - x / 2) * (1 + x**-1 * math.log(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.08, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.456, c=0.198, expected=-4.345010769099701),
        FormulaTestCase.interval_bounds(params={}, expected=(0.08, 8.0)),
    )
