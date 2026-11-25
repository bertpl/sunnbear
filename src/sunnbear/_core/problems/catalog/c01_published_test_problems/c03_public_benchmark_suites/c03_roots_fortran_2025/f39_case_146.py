"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``146`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case146(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^3 - 1.0``; the formula's interval is ``[0.51, 1.5]``.

    the comment says the bracket was changed from [0.5, 1.5], so that the first bisection step does not land on the root
    """

    number = (1, 3, 3, 39)
    name = "Case 146"
    params = ()
    location_in_publication = "root_tests.f90, case 146"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} - 1",
        interval="[0.51, 1.5]",
        summary="A cubic with 1 simple root, increasing and convex on the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.51, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.807, c=0.0, expected=-0.4744420569999999),
        FormulaTestCase.value(params={}, x=0.807, c=0.2475, expected=-0.8248539801249999),
        FormulaTestCase.interval_bounds(params={}, expected=(0.51, 1.5)),
    )
