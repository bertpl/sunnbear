"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``15`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Suhadolnik201215(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``x^2 - sin(x)^2 - 1``; the formula's interval is ``[-1, 2]``.
    """

    number = (1, 2, 11, 12)
    name = "15"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="15",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x**2 - math.sin(x) ** 2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.0, expected=-0.9999667110793792),
        FormulaTestCase.value(params={}, x=-0.1, c=0.25, expected=-0.8419222471477623),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
