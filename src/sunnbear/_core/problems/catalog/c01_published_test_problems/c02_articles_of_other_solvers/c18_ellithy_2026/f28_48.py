"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``48`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ellithy202648(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``0.05 - x^3 / ((1 - x) * (0.8 - 2*x)^2)``; the formula's interval is
    ``[0.01, 0.3]``.

    The file's note: "Chemical Equilibrium: Solving extent of reaction (Singularity at x=0.4)".
    """

    number = (1, 2, 18, 28)
    name = "48"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="48",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.29 * c
        return 0.05 - x**3 / ((1 - x) * (0.8 - 2 * x) ** 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.3)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.097, c=0.0, expected=0.04724778597175968),
        FormulaTestCase.value(params={}, x=0.097, c=0.25, expected=0.04997327048335758),
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 0.3)),
    )
