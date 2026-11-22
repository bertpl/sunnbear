"""This module holds formula f1.99.3.3.30, the modified version of the published formula f1.3.3.30.

A change of formula f1.3.3.30 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedRootsFortran20258688(Formula):
    """This formula is the modified version of formula f1.3.3.30, from roots-fortran (2025).

    The survey writes the source's function as ``((x - 13.0)*x + 47.0)*x - 36.0 - sqrt(x)``; the published intervals
    are ``[0, 2] (86), [2, 6] (87), [6, 8] (88)``.

    a different root in each bracket

    The formula holds only the test problem on ``[0, 2]``. The formula keeps that interval, evaluates the published
    function at x without shifting x, and adds ``c`` to the function's value.

    The published test problem on ``[0, 2]`` does not satisfy the benchmark suite inclusion conditions, because a shift
    along x by any ``c > 0`` evaluates ``sqrt(x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 99, 3, 3, 30)
    name = "86–88"
    params = ()
    location_in_publication = "root_tests.f90, case 86–88"
    presentation = FormulaPresentation(
        expression=r"\left(\left(\x - 13.0\right) \x + 47.0\right) \x - 36.0 - \sqrt{\x} + \c",
        interval="[0, 2]",
        notes=(
            (
                r"$\c$ shifts the function along the y-axis, not along x as for the published test "
                r"problem, because a shift along x by any $\c > 0$ evaluates $\sqrt{\x}$ left of 0, "
                "outside its domain."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return ((x - 13.0) * x + 47.0) * x - 36.0 - math.sqrt(x) + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-12.788596669241484),
        FormulaTestCase.value(params={}, x=0.0, c=-0.25, expected=-36.25),
    )
