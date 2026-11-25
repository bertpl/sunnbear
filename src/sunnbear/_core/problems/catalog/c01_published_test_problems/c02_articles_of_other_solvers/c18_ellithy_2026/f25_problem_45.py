"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``45`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem45(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(10.0 + 3.592/x^2) * (x - 0.04267) - 0.08206 * 300``; the formula's
    interval is ``[2.0, 3.0]``.

    The file's note: "Van der Waals: Volume of CO2 at P=10atm, T=300K".
    """

    number = (1, 2, 18, 25)
    name = "Problem 45"
    params = ()
    location_in_publication = "dataset.json, problem 45"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\left(10 + \frac{3.592}{\tmp{u}^{2}}\right) \left(\tmp{u} - 0.04267\right) - 0.08206 " r"\cdot 300"
        ),
        interval="[2, 3]",
        summary=(
            "The van der Waals equation for the molar volume of carbon dioxide, nearly a line on the interval, which "
            "holds the equation's only real root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (10.0 + 3.592 / x**2) * (x - 0.04267) - 0.08206 * 300

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=-0.5119345255198504),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=-2.8289761784652008),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
