"""This module holds the formula that Galdino (2011) labels f4.

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class Galdino2011F4(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``(81 - p*(108 - p*(54 - p*(12 - p))))*sign(p - 3)``, where ``p = x +
    1.11111``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 9, 4)
    name = "f4"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="f4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.0 * c
        p = x + 1.11111
        return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-0.12026429737796887),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.4952449658648378),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
