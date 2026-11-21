"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class Gsl2024Func2(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``sqrt(abs(x))*sign(x)``; the formula's interval is ``[-1/3, 1]``.

    Starting point 0.001, where the case's description says `{1.001}`; the derivative given is `1/sqrt(abs(x))`, twice
    the exact derivative
    """

    number = (1, 3, 2, 2)
    name = "func2"
    params = ()
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="func2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.33 * c
        return math.sqrt(abs(x)) * sign(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.3333333333333333, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.0666667, c=0.0, expected=0.2581989542968755),
        FormulaTestCase.value(params={}, x=0.0666667, c=0.25, expected=-0.5155902442831904),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.3333333333333333, 1.0)),
    )
