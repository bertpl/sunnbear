"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (1); P34(i)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Atkinson198928Case1(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``(x - 1)*(1 + (x - 1)^2)``; the formula's interval is ``[0, 3]``.

    Root 1. Brent's algorithm with `t = 1E-5` in IEEE single precision (Table 2.13). P34 solves cases (1)–(4) by
    bisection on `[0, 3]` with `epsilon = 1E-5`, to compare with Section 2.8.
    """

    number = (1, 4, 1, 4)
    name = "§2.8 case (1)"
    params = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (1); Problem 34(i)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\left(\tmp{u} - 1\right) \left(1 + \left(\tmp{u} - 1\right)^{2}\right)",
        interval="[0, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (x - 1) * (1 + (x - 1) ** 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-0.10099999999999998),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-1.464125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
