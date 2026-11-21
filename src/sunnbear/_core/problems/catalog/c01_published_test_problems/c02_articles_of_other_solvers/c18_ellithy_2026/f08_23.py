"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``23`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy202623(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``-0.9*x^2 + 1.7*x + 2.5``; the formula's interval is ``[2.8, 3.0]``.
    """

    number = (1, 2, 18, 8)
    name = "23"
    params = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="23",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.2 * c
        return -0.9 * x**2 + 1.7 * x + 2.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.8, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.86, c=0.0, expected=0.0003600000000004287),
        FormulaTestCase.value(params={}, x=2.86, c=0.25, expected=0.17050999999999983),
        FormulaTestCase.interval_bounds(params={}, expected=(2.8, 3.0)),
    )
