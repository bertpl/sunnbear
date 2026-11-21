"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-1(b); 2.2-1(b); 2.4-1(b); 2.5-1(b)`` in the survey of published test
problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006211B(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^5 + 2*x - 1``; the formula's interval is ``(0, 1)``.

    As 2.1-1(a).
    """

    number = (1, 4, 4, 9)
    name = "2.1-1(b)"
    params = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="Exercises 2.1-1(b), 2.2-1(b), 2.4-1(b), 2.5-1(b)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{5} + 2 \tmp{u} - 1",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**5 + 2 * x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.39757000000000003),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.8999996875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
