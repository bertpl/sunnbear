"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BadrAlmotairiElGhamry2021ProblemP10(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x*cos(x) + 1``; the formula's interval is ``[-2, 4]``.
    """

    number = (1, 2, 14, 2)
    name = "Problem P10"
    params = ()
    location_in_publication = "Table 1, P10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u} \cos{\left(\tmp{u} \right)} + 1",
        interval="[-2, 4]",
        summary="A function with 1 simple root and, 2.9 below that root, a local minimum of only 0.44.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x * math.cos(x) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.2, c=0.0, expected=0.8039866844317517),
        FormulaTestCase.value(params={}, x=-0.2, c=0.15, expected=1.2190356403023919),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 4.0)),
    )
