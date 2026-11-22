"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``83`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202583(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x - 1.0)*x^6 - 1.0``; the formula's interval is ``[0, 3]``.
    """

    number = (1, 3, 3, 28)
    name = "83"
    params = ()
    location_in_publication = "root_tests.f90, case 83"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\left(\tmp{u} - 1.0\right) \tmp{u}^{6} - 1.0",
        interval="[0, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (x - 1.0) * x**6 - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-1.0531441),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-1.00000968203125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
