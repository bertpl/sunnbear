"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class KumarSrivastav2026FunctionF2(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``x^3 + x - 1``; the formula's interval is ``[0, 1]``.

    Stated root `0.682328...`.
    """

    number = (1, 2, 19, 1)
    name = "Function f2"
    params = ()
    location_in_publication = "Table 3, f2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} + \tmp{u} - 1",
        interval="[0, 1]",
        summary="A cubic with 1 simple root, increasing and convex on the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.673),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.949875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
