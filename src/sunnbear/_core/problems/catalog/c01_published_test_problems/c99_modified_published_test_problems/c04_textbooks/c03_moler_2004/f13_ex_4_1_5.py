"""This module holds formula f1.99.4.3.13, the modified version of the published formula f1.4.3.13.

A change of formula f1.4.3.13 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedMoler2004Ex415(Formula):
    """This formula is the modified version of formula f1.4.3.13, from Moler (2004).

    The survey writes the source's function as ``1/(x - pi)``; the published interval is ``[0, 5]``.

    No root: the sign change on `[0, 5]` comes from the pole at `x = pi`.

    The formula returns 0 where ``x - c_scale*c`` equals the float of pi, the only point at which the published function
    divides by 0; everywhere else it is the published function.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because it raises
    `ZeroDivisionError` at its pole, where a solver's evaluation can land.
    """

    number = (1, 99, 4, 3, 13)
    name = "Ex. 4.1#5"
    params = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Exercise 4.1, function 5",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=(
            r"\begin{cases} 0 & \text{if } \tmp{u} = \pi \\ \frac{1}{\tmp{u} - \pi} & \text{otherwise} " r"\end{cases}"
        ),
        interval="[0, 5]",
        notes=(
            (
                r"The expression is 0 at the pole, $\tmp{u} = \pi$ in float64, where the published "
                "function divides by 0."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate f at ``x - c_scale*c``, with 0 at the pole; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        if x == math.pi:
            return 0.0
        else:
            return 1 / (x - math.pi)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.5, c=0.25, expected=-0.3458301772756758),
        FormulaTestCase.value(params={}, x=3.141592653589793, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 5.0)),
    )
