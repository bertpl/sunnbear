"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``39`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case39(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^5 - 61.0*x^4 + 6801.0/5.0*x^3 - 66531.0/5.0*x^2 + 5205601.0/100.0*x -
    4005001.0/100.0``; the formula's interval is ``[0, 10]``.
    """

    number = (1, 3, 3, 7)
    name = "Case 39"
    params = ()
    location_in_publication = "root_tests.f90, case 39"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=(
            r"\tmp{u}^{5} - 61 \tmp{u}^{4} + \frac{6801}{5} \tmp{u}^{3} - \frac{66531}{5} "
            r"\tmp{u}^{2} + \frac{5205601}{100} \tmp{u} - \frac{4005001}{100}"
        ),
        interval="[0, 10]",
        summary=(
            r"A quintic with 1 real root, a local maximum 2.4 above it, and complex roots $\x = 10 + 10 \c \pm 0.32i$ "
            r"that cause a local minimum at 0.3% of that maximum."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return (
            x**5 - 61.0 * x**4 + 6801.0 / 5.0 * x**3 - 66531.0 / 5.0 * x**2 + 5205601.0 / 100.0 * x - 4005001.0 / 100.0
        )

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.0, c=0.0, expected=28389.62),
        FormulaTestCase.value(params={}, x=3.0, c=0.25, expected=-17182.31125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 10.0)),
    )
