"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``65`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202565(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x - 1.0)^6 - 1.0``; the formula's interval is ``[1, 2.1]``.
    """

    number = (1, 3, 3, 17)
    name = "65"
    params = ()
    location_in_publication = "root_tests.f90, case 65"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.1 \c"),),
        expression=r"\left(\tmp{u} - 1.0\right)^{6} - 1.0",
        interval="[1, 2.1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.1 * c
        return (x - 1.0) ** 6 - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.33, c=0.0, expected=-0.998708532031),
        FormulaTestCase.value(params={}, x=1.33, c=0.25, expected=-0.9999999723193593),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.1)),
    )
