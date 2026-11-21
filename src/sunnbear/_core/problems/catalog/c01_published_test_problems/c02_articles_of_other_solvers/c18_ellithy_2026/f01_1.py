"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``1`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy20261(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x * exp(x) - 7``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 18, 1)
    name = "1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-2.229914332094982),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-3.999466326033678),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
