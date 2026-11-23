"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``40`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem40(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^5 - 3*x^4 + 2*x^3 - x + 0.1``; the formula's interval is ``[-1, 3]``.
    """

    number = (1, 2, 18, 21)
    name = "Problem 40"
    params = ()
    location_in_publication = "dataset.json, problem 40"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\tmp{u}^{5} - 3 \tmp{u}^{4} + 2 \tmp{u}^{3} - \tmp{u} + 0.1",
        interval="[-1, 3]",
        summary="A quintic with 3 simple roots, the lower 2 around a maximum of 0.32, against 51 at the upper bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x**5 - 3 * x**4 + 2 * x**3 - x + 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.2, c=0.0, expected=-0.08848),
        FormulaTestCase.value(params={}, x=0.2, c=0.25, expected=-1.6804800000000004),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 3.0)),
    )
