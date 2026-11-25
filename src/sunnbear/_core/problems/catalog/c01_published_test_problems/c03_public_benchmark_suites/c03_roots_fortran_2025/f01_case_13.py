"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``13`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case13(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^3 - 2.0*x - x + 3.0``; the formula's interval is ``[-3, 2]``.
    """

    number = (1, 3, 3, 1)
    name = "Case 13"
    params = ()
    location_in_publication = "root_tests.f90, case 13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{3} - 2 \tmp{u} - \tmp{u} + 3",
        interval="[-3, 2]",
        summary=(
            "A cubic with 1 real root, left of both of the cubic's local extrema, and a local minimum whose value is "
            "only 1."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**3 - 2.0 * x - x + 3.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.5, c=0.0, expected=4.125),
        FormulaTestCase.value(params={}, x=-1.5, c=0.125, expected=-9.546875),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 2.0)),
    )
