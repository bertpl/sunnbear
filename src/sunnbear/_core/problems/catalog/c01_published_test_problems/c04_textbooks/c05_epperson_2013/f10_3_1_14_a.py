"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-14(a)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson20133114A(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``1/(x^2 + 1)``; the formula's interval is ``[0, 5]``.

    No root. Bisection and regula falsi, with a comment on their behavior.
    """

    number = (1, 4, 5, 10)
    name = "3.1-14(a)"
    params = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="Exercise 3.1-14(a)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"\frac{1}{\tmp{u}^{2} + 1}",
        interval="[0, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return 1 / (x**2 + 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=0.3076923076923077),
        FormulaTestCase.value(params={}, x=1.5, c=0.25, expected=0.9411764705882353),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 5.0)),
    )
