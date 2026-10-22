"""This module holds the formula that Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026) labels f27.

The survey gives this function as an expression in a helper variable ``p``, defined beside it, not as 1 expression in x,
so a person writes this module: a change of the formula's row in `data/literature_test_problems/sources/` needs a change
of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class GanchovskiSmithRackauckasTomovTraykov2026F27(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``(81 - p(x)*(108 - p(x)*(54 - p(x)*(12 - p(x)))))*sign(p(x) - 3)``,
    where ``p(x) = x + 1.11111``; the formula's interval is ``[1, 3]``.

    ``Test Functions.pdf`` prints ``p(x) = x + 1.11``.
    """

    number = (1, 1, 13, 4)
    name = "f27"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f27",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        p = x + 1.11111
        return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-0.006965142972726102),
        FormulaTestCase.value(params={}, x=1.6, c=0.25, expected=-0.38731632624146395),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
