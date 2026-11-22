"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``73`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case73(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x - 1.0)*x*x - 1.0``; the formula's interval is ``[0, 5]``.
    """

    number = (1, 3, 3, 24)
    name = "Case 73"
    params = ()
    location_in_publication = "root_tests.f90, case 73"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"\left(\tmp{u} - 1.0\right) \tmp{u} \tmp{u} - 1.0",
        interval="[0, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return (x - 1.0) * x * x - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=0.125),
        FormulaTestCase.value(params={}, x=1.5, c=0.25, expected=-1.046875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 5.0)),
    )
