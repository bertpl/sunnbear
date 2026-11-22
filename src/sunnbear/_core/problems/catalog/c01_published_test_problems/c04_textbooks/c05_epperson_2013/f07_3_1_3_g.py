"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-3(g); 3.2-5(d); 3.3-3(b)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013313G(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``5 - x^-1``; the formula's interval is ``[0.1, 0.25]``.

    Bisection to `1E-6`; Newton from `x0 = 1/2` (3.2-5) and from `x0 = 1/4` (3.3-3).
    """

    number = (1, 4, 5, 7)
    name = "3.1-3(g)"
    params = ()
    location_in_publication = "Exercises 3.1-3(g), 3.2-5(d), 3.3-3(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.15 \c"),),
        expression=r"5 - \frac{1}{\tmp{u}}",
        interval="[0.1, 0.25]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.15 * c
        return 5 - x**-1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 0.25)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.145, c=0.0, expected=-1.8965517241379315),
        FormulaTestCase.value(params={}, x=0.145, c=0.25, expected=-4.30232558139535),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 0.25)),
    )
