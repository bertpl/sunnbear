"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``44`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202544(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``3.0*x^2*sin(x*20.0) + cos(x*2.0)``; the formula's interval is ``[-0.7,
    0.4]``.
    """

    number = (1, 3, 3, 12)
    name = "44"
    params = ()
    location_in_publication = "root_tests.f90, case 44"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.1 \c"),),
        expression=(
            r"3.0 \tmp{u}^{2} \sin{\left(\tmp{u} \cdot 20.0 \right)} + \cos{\left(\tmp{u} \cdot 2.0 " r"\right)}"
        ),
        interval="[-0.7, 0.4]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.1 * c
        return 3.0 * x**2 * math.sin(x * 20.0) + math.cos(x * 2.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.7, 0.4)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.37, c=0.0, expected=0.36936914377975283),
        FormulaTestCase.value(params={}, x=-0.37, c=0.25, expected=-0.13159178557021867),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.7, 0.4)),
    )
