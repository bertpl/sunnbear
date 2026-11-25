"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``74`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case74(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``((x - 3.0)*x - 9.0)*x - 6.0``; the formula's interval is ``[0, 8]``.
    """

    number = (1, 3, 3, 25)
    name = "Case 74"
    params = ()
    location_in_publication = "root_tests.f90, case 74"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\left(\left(\tmp{u} - 3\right) \tmp{u} - 9\right) \tmp{u} - 6",
        interval="[0, 8]",
        summary=(
            "A cubic that falls from a local maximum of $-1$ to a local minimum and then rises steeply, with 1 simple "
            "root on the rise."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return ((x - 3.0) * x - 9.0) * x - 6.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.4, c=0.0, expected=-31.056),
        FormulaTestCase.value(params={}, x=2.4, c=0.2, expected=-10.015999999999998),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 8.0)),
    )
