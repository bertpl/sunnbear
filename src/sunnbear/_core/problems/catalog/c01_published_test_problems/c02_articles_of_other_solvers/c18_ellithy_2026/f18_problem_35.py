"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``35`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem35(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^25 - 1``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 18, 18)
    name = "Problem 35"
    params = ()
    location_in_publication = "dataset.json, problem 35"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}^{25} - 1",
        interval="[0, 2]",
        summary=(
            "A function within 0.004 of $-1$ up to 0.2 below the function's 1 root, and above 90 from 0.2 above that "
            "root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**25 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.999997156971197),
        FormulaTestCase.value(params={}, x=1.4, c=0.25, expected=-0.9282102012308149),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
