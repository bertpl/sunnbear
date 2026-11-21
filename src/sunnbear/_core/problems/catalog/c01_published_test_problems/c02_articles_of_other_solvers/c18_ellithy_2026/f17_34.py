"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``34`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202634(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``4*sin(x) - x + 1``; the formula's interval is ``[-1, 0]``.
    """

    number = (1, 2, 18, 17)
    name = "34"
    params = ()
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="dataset.json, problem 34",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"4 \sin{\left(\tmp{u} \right)} - \tmp{u} + 1",
        interval="[-1, 0]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 4 * math.sin(x) - x + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=-0.8768707489507641),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=-1.303662019157495),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
