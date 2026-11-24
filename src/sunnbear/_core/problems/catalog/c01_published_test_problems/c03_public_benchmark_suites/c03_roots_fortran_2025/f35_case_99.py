"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``99`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case99(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``cos(x) + x``; the formula's interval is ``[-10, 10]``.

    the block's comment adds "see also #26"; Stage §3.5 with `x` replaced by `-x`
    """

    number = (1, 3, 3, 35)
    name = "Case 99"
    params = ()
    location_in_publication = "root_tests.f90, case 99"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} + \tmp{u}",
        interval="[-10, 10]",
        summary=(
            r"An increasing function with 3 or 4 inflections of slope 0 on the interval and 1 root, at $\x = 20 \c - "
            r"d$, where $d$ is the fixed point of the cosine."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return math.cos(x) + x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=-4.653643620863612),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=-9.911130261884677),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
