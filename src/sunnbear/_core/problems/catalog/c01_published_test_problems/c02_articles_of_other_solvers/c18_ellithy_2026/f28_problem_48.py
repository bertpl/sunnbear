"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``48`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem48(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``0.05 - x^3 / ((1 - x) * (0.8 - 2*x)^2)``; the formula's interval is
    ``[0.01, 0.3]``.

    The file's note: "Chemical Equilibrium: Solving extent of reaction (Singularity at x=0.4)".
    """

    number = (1, 2, 18, 28)
    name = "Problem 48"
    params = ()
    location_in_publication = "dataset.json, problem 48"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.29 \c"),),
        expression=r"0.05 - \frac{\tmp{u}^{3}}{\left(1 - \tmp{u}\right) \left(0.8 - 2 \tmp{u}\right)^{2}}",
        interval="[0.01, 0.3]",
        summary=(
            r"An equilibrium equation for a reaction's extent, nearly flat around $\x = 0.29 \c$ and falling steeply "
            r"toward a double pole 0.21 above the root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.29 * c
        return 0.05 - x**3 / ((1 - x) * (0.8 - 2 * x) ** 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.3)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.097, c=0.0, expected=0.04724778597175968),
        FormulaTestCase.value(params={}, x=0.097, c=0.25, expected=0.04997327048335758),
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 0.3)),
    )
