"""This module holds a formula of Chen, Li (2006).

The formula comes from the row with the key ``4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ChenLi20064(Formula):
    """This formula comes from Chen, Li (2006).

    The survey writes the source's function as ``x*exp(-x) - 0.1``; the formula's interval is ``[0, 1]``.

    `x0 = 1`. Root 0.111833.
    """

    number = (1, 2, 6, 3)
    name = "4"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Chen, J., Li, W. (2007). An improved exponential regula falsi methods with quadratic "
            "convergence of both diameter and point for solving nonlinear equations. Applied Numerical "
            "Mathematics 57(1), 80–88. Published online 14 February 2006. "
            "https://doi.org/10.1016/j.apnum.2006.01.001. The article prints the volume and the year "
            "2007 but no issue number; the issue number is Crossref's. The year 2006 of the title "
            "follows the online date that the article prints; the issue is dated 2007."
        ),
        location="4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(-x) - 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.12224546620451536),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.052438528774964306),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
