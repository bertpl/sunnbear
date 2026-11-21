"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``43`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy202643(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``-2 * log10(0.000027027 + (2.51 / (10000000 * sqrt(x)))) - 1/sqrt(x)``;
    the formula's interval is ``[0.008, 0.03]``.

    Written `log(..., 10)` in the file, a base-10 log. The file's note: "Colebrook-White: Friction factor for Re=1e7,
    e/D=0.0001". The article (p. 104) prints the constant as `2.7*10^-5`; the row keeps the file's `0.000027027`, which
    is `0.0001/3.7` rounded to 5 significant digits, because only that constant reproduces the bisection count of 49
    that Table 12 gives for this problem: the printed constant gives 46.
    """

    number = (1, 2, 18, 24)
    name = "43"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="43",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.022 * c
        return -2 * math.log10(0.000027027 + (2.51 / (10000000 * math.sqrt(x)))) - 1 / math.sqrt(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.008, 0.03)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.0146, c=0.0, expected=0.7960270724390422),
        FormulaTestCase.value(params={}, x=0.0146, c=0.25, expected=-1.427137798069988),
        FormulaTestCase.interval_bounds(params={}, expected=(0.008, 0.03)),
    )
