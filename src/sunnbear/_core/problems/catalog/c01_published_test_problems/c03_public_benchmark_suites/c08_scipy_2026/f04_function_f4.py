"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Scipy2026FunctionF4(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``1.0 + .1*x`` (x > 1); ``-1.0 + .1*x`` (x < 1); ``0`` (x = 1); the
    formula's interval is ``[0.5, sqrt(3)]``.

    ID original.04.00; smoothness -1; no derivatives
    """

    number = (1, 3, 8, 4)
    name = "Function f4"
    params = ()
    location_in_publication = "Collection “original”, f4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.23 \c"),),
        expression=(
            r"\begin{cases} "
            r"1 + 0.1 \tmp{u} & \text{if } \tmp{u} > 1 \\ "
            r"-1 + 0.1 \tmp{u} & \text{if } \tmp{u} < 1 \\ "
            r"0 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[0.5, \sqrt{3}]",
        summary=(
            r"A piecewise linear function that jumps from $-0.9$ to $1.1$ at its root, the only value of $\x$ where it "
            "is 0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.23 * c
        if x > 1.0:
            return 1.0 + 0.1 * x
        elif x < 1.0:
            return -1.0 + 0.1 * x
        else:
            return 0.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=-0.9130385),
        FormulaTestCase.value(params={}, x=0.869615, c=0.25, expected=-0.9437885),
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=1.15),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
