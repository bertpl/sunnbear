"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``37`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case37(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^3 - 5.0*x^2 + 12.0*x - 8.0``; the formula's interval is ``[-10,
    10]``.
    """

    number = (1, 3, 3, 5)
    name = "Case 37"
    params = ()
    location_in_publication = "root_tests.f90, case 37"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\tmp{u}^{3} - 5.0 \tmp{u}^{2} + 12.0 \tmp{u} - 8.0",
        interval="[-10, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return x**3 - 5.0 * x**2 + 12.0 * x - 8.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=-200.0),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=-1250.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
