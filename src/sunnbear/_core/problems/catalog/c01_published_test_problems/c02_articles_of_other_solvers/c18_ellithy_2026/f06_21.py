"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``21`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202621(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(x^2 - 4)*(x + 1.5)*(x - 0.5)``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 18, 6)
    name = "21"
    params = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="dataset.json, problem 21",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u}^{2} - 4\right) \left(\tmp{u} + 1.5\right) \left(\tmp{u} - 0.5\right)",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x**2 - 4) * (x + 1.5) * (x - 0.5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.7643999999999999),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=2.5536000000000003),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
