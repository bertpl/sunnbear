"""This module holds a formula of Gottlieb, Thompson (2010).

The formula comes from the row with the key ``1`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class GottliebThompson20101(Formula):
    """This formula comes from Gottlieb, Thompson (2010).

    The survey writes the source's function as ``3*sin(x) - 2``; the formula's interval is ``[0, 1]``.

    Table 2's root `0.7297276562`.
    """

    number = (1, 2, 8, 1)
    name = "1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Gottlieb, R. G., Thompson, B. F. (2010). Bisected direct quadratic regula falsi. Applied "
            "Mathematical Sciences 4(15), 709–718. No DOI; the publisher's copy: "
            "http://www.m-hikari.com/ams/ams-2010/ams-13-16-2010/gottliebAMS13-16-2010.pdf."
        ),
        location="1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 3 * math.sin(x) - 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-1.1134393800159814),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-1.8500624921879651),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
