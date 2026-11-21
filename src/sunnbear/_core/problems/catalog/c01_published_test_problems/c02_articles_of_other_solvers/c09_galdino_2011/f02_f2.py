"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f2`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Galdino2011F2(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``(x - 4)^5*log(x)``; the formula's interval is ``[3.5, 4.5]``.

    The article prints `ln`. The appendix states a zero of multiplicity 5 at `x = 4`.
    """

    number = (1, 2, 9, 2)
    name = "f2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="f2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x - 4) ** 5 * math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.5, 4.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.8, c=0.0, expected=-0.0004272003413543507),
        FormulaTestCase.value(params={}, x=3.8, c=0.25, expected=-0.02337874657447599),
        FormulaTestCase.interval_bounds(params={}, expected=(3.5, 4.5)),
    )
