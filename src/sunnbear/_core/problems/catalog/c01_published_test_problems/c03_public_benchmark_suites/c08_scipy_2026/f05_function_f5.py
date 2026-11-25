"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Scipy2026FunctionF5(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``1.0/(1. - x)`` (x != 1); ``0`` (x = 1); the formula's interval is
    ``[0.5, sqrt(3)]``.

    ID original.05.00; smoothness -1; no derivatives
    """

    number = (1, 3, 8, 5)
    name = "Function f5"
    params = ()
    location_in_publication = "Collection “original”, f5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } \tmp{u} = 1 \\ "
            r"\frac{1}{1 - \tmp{u}} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[0.5, \sqrt{3}]",
        summary=(
            "A hyperbola that changes sign only at its pole, from large positive to large negative values, with its "
            "value at the pole set to 0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        if x == 1.0:
            return 0.0
        else:
            return 1.0 / (1.0 - x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=7.669593895003261),
        FormulaTestCase.value(params={}, x=0.869615, c=0.3075, expected=2.2837046256437192),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
