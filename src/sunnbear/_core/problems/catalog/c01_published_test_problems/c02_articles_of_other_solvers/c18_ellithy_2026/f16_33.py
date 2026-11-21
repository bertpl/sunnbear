"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``33`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy202633(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 - 10*x^3 + 35*x^2 - 50*x + 24``; the formula's interval is ``[0,
    1.5]``.
    """

    number = (1, 2, 18, 16)
    name = "33"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="33",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return x**4 - 10 * x**3 + 35 * x**2 - 50 * x + 24

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=7.71725625),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=20.442687890625),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
