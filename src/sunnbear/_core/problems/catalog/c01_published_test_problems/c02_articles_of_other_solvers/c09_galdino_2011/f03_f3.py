"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Galdino2011F3(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``(sin(x) - x/4)^3``; the formula's interval is ``[2, 3]``.
    """

    number = (1, 2, 9, 3)
    name = "f3"
    params = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="f3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (math.sin(x) - x / 4) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=0.004974395881789984),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=0.05267633307479046),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
