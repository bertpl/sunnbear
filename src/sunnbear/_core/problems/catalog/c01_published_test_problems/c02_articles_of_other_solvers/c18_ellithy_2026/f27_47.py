"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``47`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy202647(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``cos(x) + 1.0 * (1 - cos(x))^2 - 0.05 * x^2``; the formula's interval is
    ``[3.0, 6.0]``.

    The file's note: "Beam Deflection (Non-linear transcendental)".
    """

    number = (1, 2, 18, 27)
    name = "47"
    params = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="47",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.cos(x) + 1.0 * (1 - math.cos(x)) ** 2 - 0.05 * x**2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.9, c=0.0, expected=1.4924100144814652),
        FormulaTestCase.value(params={}, x=3.9, c=0.25, expected=2.5037689766630495),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 6.0)),
    )
