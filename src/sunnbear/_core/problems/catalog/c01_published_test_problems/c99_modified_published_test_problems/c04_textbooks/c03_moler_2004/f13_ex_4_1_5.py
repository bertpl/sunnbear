"""This module holds formula f1.99.4.3.13, the modified version of the published formula f1.4.3.13.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.13 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedMoler2004Ex415(Formula):
    """This formula is the modified version of formula f1.4.3.13, from Moler (2004).

    The survey writes the source's function as ``1/(x - pi)``; the published interval is ``[0, 5]``.

    No root: the sign change on `[0, 5]` comes from the pole at `x = pi`.

    The formula returns 0 where ``x - c_scale*c`` equals the float of pi, the 1 point at which the published function
    divides by 0; everywhere else it is the published function.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because it raises
    `ZeroDivisionError` at its pole, where a solver's evaluation can land.
    """

    number = (1, 99, 4, 3, 13)
    name = "Ex. 4.1#5"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Ex. 4.1#5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, with 0 at the pole; category 1 states ``c_scale``."""
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
