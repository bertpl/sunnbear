"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Scipy2026FunctionF3(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``x*(x - 1.)*(x - 2.)*(x - 3.)``; the formula's interval is ``[0.5,
    sqrt(3)]``.

    ID original.03.00; derivatives given
    """

    number = (1, 3, 8, 3)
    name = "Function f3"
    params = ()
    location_in_publication = "Collection “original”, f3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} \left(\tmp{u} - 1\right) \left(\tmp{u} - 2\right) \left(\tmp{u} - 3\right)",
        interval=r"[0.5, \sqrt{3}]",
        summary="A quartic with 1 of its 4 simple roots on the interval, and a local maximum 0.5 above that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * (x - 1.0) * (x - 2.0) * (x - 3.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=-0.2730480850556551),
        FormulaTestCase.value(params={}, x=0.869615, c=0.3075, expected=-0.8628247840057047),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
