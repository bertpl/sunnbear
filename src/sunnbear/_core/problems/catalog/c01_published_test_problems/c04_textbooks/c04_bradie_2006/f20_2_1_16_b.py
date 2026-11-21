"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-16(b); 2.2-11(b); 2.3-15; 2.4-14(b); 2.5-18(b)`` in the survey of
published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Bradie20062116B(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^3 - x^2 - 10*x + 7``; the formula's interval is `(0, 1)` (2.3-15).

    All real roots to `1E-6` by bisection, false position, Newton and secant. 2.3-15 compares 3 fixed-point iteration
    functions of the reader's choice for its unique zero on `(0, 1)`.
    """

    number = (1, 4, 4, 20)
    name = "2.1-16(b)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="2.1-16(b); 2.2-11(b); 2.3-15; 2.4-14(b); 2.5-18(b)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - x**2 - 10 * x + 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=3.9370000000000003),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=6.497625),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
