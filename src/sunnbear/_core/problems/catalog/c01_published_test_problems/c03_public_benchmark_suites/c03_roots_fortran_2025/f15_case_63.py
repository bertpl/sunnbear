"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``63`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case63(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^3 + 4.0*x^2 - 10.0``; the formula's interval is ``[0, 1.5]``.
    """

    number = (1, 3, 3, 15)
    name = "Case 63"
    params = ()
    location_in_publication = "root_tests.f90, case 63"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\tmp{u}^{3} + 4.0 \tmp{u}^{2} - 10.0",
        interval="[0, 1.5]",
        summary=r"A cubic with a local minimum at $\x = 1.5 \c$ and 1 root 1.37 above that minimum.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return x**3 + 4.0 * x**2 - 10.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-9.098875),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=-9.977078125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
