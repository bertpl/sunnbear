"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Gsl2024Func4(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x*exp(-x)``; the formula's interval is ``[-1/3, 2]``.

    Starting point -2; expected failure from starting point 2, described as "max iterations x -> +Inf"; derivative given
    """

    number = (1, 3, 2, 4)
    name = "func4"
    params = ()
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="func4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.33 * c
        return x * math.exp(-x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.3333333333333333, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.366667, c=0.0, expected=0.2541150403402077),
        FormulaTestCase.value(params={}, x=0.366667, c=0.25, expected=-0.26782611907005804),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.3333333333333333, 2.0)),
    )
