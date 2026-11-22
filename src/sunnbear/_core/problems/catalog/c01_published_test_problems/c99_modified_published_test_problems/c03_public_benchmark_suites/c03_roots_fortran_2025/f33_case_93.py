"""This module holds formula f1.99.3.3.33, the modified version of the published formula f1.3.3.33.

A change of formula f1.3.3.33 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedRootsFortran2025Case93(Formula):
    """This formula is the modified version of formula f1.3.3.33, from roots-fortran (2025).

    The survey writes the source's function as ``(x - 10.0)*x + 23.0 - x^0.4``; the published intervals are ``[0, 6]
    (93), [6, 8] (94)``.

    a different root in each bracket

    The formula holds only the test problem on ``[0, 6]``. The formula keeps that interval, evaluates the published
    function at x without shifting x, and adds ``c`` to the function's value.

    The published test problem on ``[0, 6]`` does not satisfy the benchmark suite inclusion conditions, because a shift
    along x by any ``c > 0`` evaluates ``x^0.4`` left of ``a = 0``, where it is not real.
    """

    number = (1, 99, 3, 3, 33)
    name = "Case 93"
    params = ()
    location_in_publication = "root_tests.f90, case 93–94"
    presentation = FormulaPresentation(
        expression=r"\left(\x - 10.0\right) \x + 23.0 - \x^{0.4} + \c",
        interval="[0, 6]",
        notes=(
            (
                r"$\c$ shifts the function along the y-axis, not along x as for the published test "
                r"problem, because a shift along x by any $\c > 0$ evaluates $\x^{0.4}$ left of 0, where "
                "it is not real."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return (x - 10.0) * x + 23.0 - x**0.4 + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.8, c=0.25, expected=7.22494618097175),
        FormulaTestCase.value(params={}, x=0.0, c=-0.25, expected=22.75),
    )
