"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``40`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case40(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x - 1.0)^5``; the formula's interval is ``[0, 10]``.
    """

    number = (1, 3, 3, 8)
    name = "Case 40"
    params = ()
    location_in_publication = "root_tests.f90, case 40"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\left(\tmp{u} - 1.0\right)^{5}",
        interval="[0, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return (x - 1.0) ** 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.0, c=0.0, expected=32.0),
        FormulaTestCase.value(params={}, x=3.0, c=0.25, expected=-0.03125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 10.0)),
    )
