"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Galdino2011F5(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``sin((x - 7.143)^3)``; the formula's interval is ``[7, 8]``.

    The appendix states a zero of multiplicity 3 at `x = 7.143`.
    """

    number = (1, 2, 9, 5)
    name = "f5"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="f5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin((x - 7.143) ** 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (7.0, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=7.3, c=0.0, expected=0.0038698833407079616),
        FormulaTestCase.value(params={}, x=7.3, c=0.25, expected=-0.0008043569132648269),
        FormulaTestCase.interval_bounds(params={}, expected=(7.0, 8.0)),
    )
