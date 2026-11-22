"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Scipy2026FunctionF2(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``x^2 - 1``; the formula's interval is ``[0.5, sqrt(3)]``.

    ID original.02.00; derivatives given
    """

    number = (1, 3, 8, 2)
    name = "Function f2"
    params = ()
    location_in_publication = "Collection “original”, f2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.23 \c"),),
        expression=r"\tmp{u}^{2} - 1",
        interval=r"[0.5, \sqrt{3}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.23 * c
        return x**2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=-0.24376975177499996),
        FormulaTestCase.value(params={}, x=0.869615, c=0.25, expected=-0.684026726775),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
