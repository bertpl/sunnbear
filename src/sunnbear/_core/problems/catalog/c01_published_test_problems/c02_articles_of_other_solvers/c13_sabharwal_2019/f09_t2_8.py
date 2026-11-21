"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Sabharwal2019T28(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x*exp(x) - 7``; the formula's interval is ``[-1, 1]``.

    Printed `xe^x - 7`. No sign change and no root on `[-1, 1]`: the only real root is about `1.5243`.
    """

    number = (1, 2, 13, 9)
    name = "T2.8"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-7.268128018414256),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-7.365912693766539),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
